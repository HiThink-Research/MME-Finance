from functools import partial

from .image_base import ImageBaseDataset
from .utils import build_judge, DEBUG_MESSAGE
from ..smp import *
from ..utils import track_progress_rich


class ImageVQADataset(ImageBaseDataset):
    TYPE = 'VQA'

    DATASET_URL = {
        'OCRVQA_TEST': 'https://opencompass.openxlab.space/utils/VLMEval/OCRVQA_TEST.tsv',
        'OCRVQA_TESTCORE': 'https://opencompass.openxlab.space/utils/VLMEval/OCRVQA_TESTCORE.tsv',
        'TextVQA_VAL': 'https://opencompass.openxlab.space/utils/VLMEval/TextVQA_VAL.tsv',
        'DocVQA_VAL': 'https://opencompass.openxlab.space/utils/VLMEval/DocVQA_VAL.tsv',
        'DocVQA_TEST': 'https://opencompass.openxlab.space/utils/VLMEval/DocVQA_TEST.tsv',
        'InfoVQA_VAL': 'https://opencompass.openxlab.space/utils/VLMEval/InfoVQA_VAL.tsv',
        'InfoVQA_TEST': 'https://opencompass.openxlab.space/utils/VLMEval/InfoVQA_TEST.tsv',
        'ChartQA_TEST': 'https://opencompass.openxlab.space/utils/VLMEval/ChartQA_TEST.tsv',
        'GQA_TestDev_Balanced': 'https://opencompass.openxlab.space/utils/VLMEval/GQA_TestDev_Balanced.tsv',
    }

    DATASET_MD5 = {
        'OCRVQA_TEST': 'ca46a6d74b403e9d6c0b670f6fc00db9',
        'OCRVQA_TESTCORE': 'c5239fe77db8bdc1f2ad8e55e0d1fe97',
        'TextVQA_VAL': 'b233b31f551bbf4056f2f955da3a92cd',
        'DocVQA_VAL': 'd5ee77e1926ff10690d469c56b73eabf',
        'DocVQA_TEST': '6a2f28cac26ef2d3447374e8c6f6c8e9',
        'InfoVQA_VAL': '2342e9c225222f0ef4dec545ebb126fe',
        'InfoVQA_TEST': 'df535bf51b88dc9718252c34131a6227',
        'ChartQA_TEST': 'c902e0aa9be5582a7aad6dcf52734b42',
        'GQA_TestDev_Balanced': 'fead7df22befc1ed3ca2b62ea26fa17b',
    }

    def build_prompt(self, line):
        msgs = super().build_prompt(line)
        assert msgs[-1]['type'] == 'text'
        msgs[-1]['value'] += '\nAnswer the question using a single word or phrase.'
        return msgs

    # It returns a DataFrame
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.vqa_eval import hit_calculate, process_line

        data = load(eval_file)
        dataset = self.dataset_name
        assert 'answer' in data and 'prediction' in data
        data['prediction'] = [str(x) for x in data['prediction']]
        data['answer'] = [str(x) for x in data['answer']]
        lt = len(data)
        pool = mp.Pool(16)
        lines = [data.iloc[i] for i in range(lt)]
        if listinstr(['TextVQA'], dataset):
            res = pool.map(partial(process_line, method='vqa_score'), lines)
        elif listinstr(['ChartQA'], dataset):
            res = pool.map(partial(process_line, method='relaxed_accuracy'), lines)
        elif listinstr(['OCRVQA', 'GQA'], dataset):
            res = pool.map(partial(process_line, method='accuracy'), lines)
        elif listinstr(['DocVQA', 'InfoVQA'], dataset):
            res = pool.map(partial(process_line, method='anls'), lines)
        else:  # default using vqa_score to calculate score
            res = pool.map(process_line, lines)
        hit = hit_calculate(res, dataset)
        ret = dict()
        if 'split' in data:
            splits = set(data['split'])
            for sp in splits:
                sub = [r for l, r in zip(lines, res) if l['split'] == sp]
                # [np.mean(x['match']) >= full_score_weight for x in sub]
                hit = hit_calculate(sub, dataset)
                ret[sp] = np.mean(hit) * 100
            sub = [r for l, r in zip(lines, res)]
            hit = hit_calculate(sub, dataset)
            ret['Overall'] = np.mean(hit) * 100
        else:
            ret['Overall'] = np.mean(hit) * 100
            if 'category' in data:
                cates = list(set(data['category']))
                cates.sort()
                for c in cates:
                    sub = [r for l, r in zip(lines, res) if l['category'] == c]
                    # [np.mean(x['match']) >= full_score_weight for x in sub]
                    hit = hit_calculate(sub, dataset)
                    ret[c] = np.mean(hit) * 100
        ret = d2df(ret)
        ret.round(2)

        suffix = eval_file.split('.')[-1]
        result_file = eval_file.replace(f'.{suffix}', '_acc.csv')
        dump(ret, result_file)
        return ret


class OCRBench(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'OCRBench': 'https://opencompass.openxlab.space/utils/VLMEval/OCRBench.tsv'
    }
    DATASET_MD5 = {'OCRBench': 'e953d98a987cc6e26ef717b61260b778'}

    # It returns a dictionary
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        OCRBench_score = {
            'Regular Text Recognition': 0,
            'Irregular Text Recognition': 0,
            'Artistic Text Recognition': 0,
            'Handwriting Recognition': 0,
            'Digit String Recognition': 0,
            'Non-Semantic Text Recognition': 0,
            'Scene Text-centric VQA': 0,
            'Doc-oriented VQA': 0,
            'Key Information Extraction': 0,
            'Handwritten Mathematical Expression Recognition': 0,
        }

        data = load(eval_file)
        lt = len(data)
        lines = [data.iloc[i] for i in range(lt)]
        for i in tqdm(range(len(lines))):
            line = lines[i]
            predict = str(line['prediction'])
            answers = eval(line['answer'])
            category = line['category']
            if category == 'Handwritten Mathematical Expression Recognition':
                for j in range(len(answers)):
                    answer = answers[j].strip().replace('\n', ' ').replace(' ', '')
                    predict = predict.strip().replace('\n', ' ').replace(' ', '')
                    if answer in predict:
                        OCRBench_score[category] += 1
                        break
            else:
                for j in range(len(answers)):
                    answer = answers[j].lower().strip().replace('\n', ' ')
                    predict = predict.lower().strip().replace('\n', ' ')
                    if answer in predict:
                        OCRBench_score[category] += 1
                        break

        final_score_dict = {}
        final_score_dict['Text Recognition'] = \
            (OCRBench_score['Regular Text Recognition'] + OCRBench_score['Irregular Text Recognition']
             + OCRBench_score['Artistic Text Recognition'] + OCRBench_score['Handwriting Recognition']
             + OCRBench_score['Digit String Recognition'] + OCRBench_score['Non-Semantic Text Recognition'])
        final_score_dict['Scene Text-centric VQA'] = OCRBench_score['Scene Text-centric VQA']
        final_score_dict['Doc-oriented VQA'] = OCRBench_score['Doc-oriented VQA']
        final_score_dict['Key Information Extraction'] = OCRBench_score['Key Information Extraction']
        final_score_dict['Handwritten Mathematical Expression Recognition'] = \
            (OCRBench_score['Handwritten Mathematical Expression Recognition'])
        final_score_dict['Final Score'] = \
            (final_score_dict['Text Recognition'] + final_score_dict['Scene Text-centric VQA']
             + final_score_dict['Doc-oriented VQA'] + final_score_dict['Key Information Extraction']
             + final_score_dict['Handwritten Mathematical Expression Recognition'])
        final_score_dict['Final Score Norm'] = (float(final_score_dict['Final Score']) / 10)
        score_pth = eval_file.replace('.xlsx', '_score.json')
        dump(final_score_dict, score_pth)
        return final_score_dict


class MathVista(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'MathVista_MINI': 'https://opencompass.openxlab.space/utils/VLMEval/MathVista_MINI.tsv'
    }
    DATASET_MD5 = {'MathVista_MINI': 'f199b98e178e5a2a20e7048f5dcb0464'}

    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.mathvista import MathVista_auxeval, MathVista_acc

        model = judge_kwargs['model']
        suffix = eval_file.split('.')[-1]
        storage = eval_file.replace(f'.{suffix}', f'_{model}.xlsx')
        tmp_file = eval_file.replace(f'.{suffix}', f'_{model}.pkl')
        nproc = judge_kwargs.pop('nproc', 4)

        if not osp.exists(storage):
            data = load(eval_file)
            model = build_judge(max_tokens=128, **judge_kwargs)
            assert model.working(), ('MathVista evaluation requires a working OPENAI API\n' + DEBUG_MESSAGE)
            lt = len(data)
            lines = [data.iloc[i] for i in range(lt)]
            tups = [(model, line) for line in lines]
            indices = [line['index'] for line in lines]

            ans = {}
            if osp.exists(tmp_file):
                ans = load(tmp_file)
            tups = [x for x, i in zip(tups, indices) if i not in ans]
            indices = [i for i in indices if i not in ans]

            if len(indices):
                new_results = track_progress_rich(
                    MathVista_auxeval,
                    tups,
                    nproc=nproc,
                    chunksize=nproc,
                    keys=indices,
                    save=tmp_file,
                )
                ans = load(tmp_file)
                for k, v in zip(indices, new_results):
                    assert k in ans
                    assert ans[k]['log'] == v['log'] and ans[k]['res'] == v['res']

            data['res'] = [ans[idx]['res'] for idx in data['index']]
            data['log'] = [ans[idx]['log'] for idx in data['index']]
            dump(data, storage)

        score = MathVista_acc(storage)
        score_pth = storage.replace('.xlsx', '_score.csv')
        dump(score, score_pth)
        return score


class MathVision(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'MathVision': 'https://opencompass.openxlab.space/utils/VLMEval/MathVision.tsv',
        'MathVision_MINI': 'https://opencompass.openxlab.space/utils/VLMEval/MathVision_MINI.tsv'
    }
    DATASET_MD5 = {
        'MathVision': '93f6de14f7916e598aa1b7165589831e',
        'MathVision_MINI': '060fe4fa5d868987ce179307bd5f8a33'
    }

    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.mathv import MATH_V_auxeval, MATH_V_acc

        if 'model' in judge_kwargs:
            model = judge_kwargs['model']
        else:
            model = os.path.basename(os.environ.get('LOCAL_LLM'))
        suffix = eval_file.split('.')[-1]
        storage = eval_file.replace(f'.{suffix}', f'_{model}.xlsx')
        tmp_file = eval_file.replace(f'.{suffix}', f'_{model}.pkl')
        nproc = judge_kwargs.pop('nproc', 4)

        if not osp.exists(storage):
            data = load(eval_file)
            model = build_judge(max_tokens=128, **judge_kwargs)
            assert model.working(), ('MATH-Vision evaluation requires a working OPENAI API\n' + DEBUG_MESSAGE)
            lt = len(data)
            lines = [data.iloc[i] for i in range(lt)]
            tups = [(model, line) for line in lines]
            indices = [line['index'] for line in lines]

            ans = {}
            if osp.exists(tmp_file):
                ans = load(tmp_file)
            tups = [x for x, i in zip(tups, indices) if i not in ans]
            indices = [i for i in indices if i not in ans]

            if len(indices):
                new_results = track_progress_rich(
                    MATH_V_auxeval,
                    tups,
                    nproc=nproc,
                    chunksize=nproc,
                    keys=indices,
                    save=tmp_file,
                )
                ans = load(tmp_file)
                for k, v in zip(indices, new_results):
                    assert k in ans
                    assert ans[k]['log'] == v['log'] and ans[k]['res'] == v['res']

            data['res'] = [ans[idx]['res'] for idx in data['index']]
            data['log'] = [ans[idx]['log'] for idx in data['index']]
            dump(data, storage)

        score = MATH_V_acc(storage)
        score_pth = storage.replace('.xlsx', '_score.csv')
        dump(score, score_pth)
        return score


class LLaVABench(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {'LLaVABench': 'https://opencompass.openxlab.space/utils/VLMEval/LLaVABench.tsv'}
    DATASET_MD5 = {'LLaVABench': 'd382a093f749a697820d3dadd61c8428'}

    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.llavabench import (
            build_prompt,
            LLaVABench_atomeval,
            LLaVABench_score,
        )

        suffix = '.' + eval_file.split('.')[-1]
        record_file = eval_file.replace(suffix, '_openai_result' + suffix)
        score_file = eval_file.replace(suffix, '_score.csv')
        nproc = judge_kwargs.pop('nproc', 4)
        system_prompt = 'You are a helpful and precise assistant for checking the quality of the answer.'

        if not osp.exists(record_file):
            data = load(eval_file)
            lines = [data.iloc[i] for i in range(len(data))]
            model = build_judge(temperature=0.2, system_prompt=system_prompt, **judge_kwargs)
            assert model.working(), ('LLaVABench evaluation requires a working OPENAI API\n' + DEBUG_MESSAGE)

            prompts = [build_prompt(line) for line in lines]
            tups = [(model, prompt) for prompt in prompts]
            scores = track_progress_rich(LLaVABench_atomeval, tups, nproc=nproc, chunksize=nproc)
            data['gpt4_score'] = [x[0] for x in scores]
            data['score'] = [x[1] for x in scores]
            dump(data, record_file)

        data = load(record_file)
        ret = LLaVABench_score(data).round(1)
        dump(ret, score_file)
        return ret


class MMVet(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'MMVet': 'https://opencompass.openxlab.space/utils/VLMEval/MMVet.tsv'
    }
    DATASET_MD5 = {'MMVet': '748aa6d4aa9d4de798306a63718455e3'}

    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.mmvet import MMVet_auxeval, MMVet_acc

        suffix = eval_file.split('.')[-1]
        model = judge_kwargs['model']
        storage = eval_file.replace(f'.{suffix}', f'_{model}.xlsx')
        tmp_file = eval_file.replace(f'.{suffix}', f'_{model}.pkl')
        nproc = judge_kwargs.pop('nproc', 4)
        if not osp.exists(storage):
            data = load(eval_file)
            model = build_judge(max_tokens=3, **judge_kwargs)
            assert model.working(), ('MMVet evaluation requires a working OPENAI API\n' + DEBUG_MESSAGE)

            lt = len(data)
            lines = [data.iloc[i] for i in range(lt)]
            tups = [(model, line) for line in lines]
            indices = [line['index'] for line in lines]

            ans = load(tmp_file) if osp.exists(tmp_file) else {}
            tups = [x for x, i in zip(tups, indices) if i not in ans]
            indices = [i for i in indices if i not in ans]

            if len(indices):
                new_results = track_progress_rich(
                    MMVet_auxeval,
                    tups,
                    nproc=nproc,
                    chunksize=nproc,
                    keys=indices,
                    save=tmp_file,
                )
                ans = load(tmp_file)
                for k, v in zip(indices, new_results):
                    assert k in ans
                    assert ans[k]['log'] == v['log'] and ans[k]['score'] == v['score']
            data['score'] = [ans[idx]['score'] for idx in data['index']]
            data['log'] = [ans[idx]['log'] for idx in data['index']]
            dump(data, storage)

        score, score_fine = MMVet_acc(storage)
        score_pth = storage.replace('.xlsx', '_score.csv')
        score_fine_pth = storage.replace('.xlsx', '_score_fine.csv')
        dump(score, score_pth)
        dump(score_fine, score_fine_pth)
        return score

class MMfin(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'MMfin': 'https://opencompass.openxlab.space/utils/VLMEval/MMfin.tsv'
    }
    DATASET_MD5 = {'MMfin': '748aa6d4aa9d4de798306a63718455e3'}

    def build_prompt(self, line):
        if isinstance(line, int):
            line = self.data.iloc[line]

        tgt_path = line['image_path']
        root = LMUDataRoot()
        tgt_path = osp.join(root, 'images/MMfin', tgt_path)

        prompt = 'You are a financial expert who is well-versed in various financial charts and has extensive financial knowledge. Now you are given a image and corresponding question. Please answer this question.'
        prompt += '/nThis is question: '
        prompt += line['question']
        prompt += '/nHere are the answer requirements: '
        format_prompt = {
            'Image Caption':'Describe this image in whole-part structure. Start with a sentence summarizing the main theme of the image. If the image describes multiple objects, firstly introduce each object in one sentence, and if there are some connections between objects, explain every connection in one sentence. If the object is complex, it can be further explained. Your answer should be less than 250 words and should not include any irrelevant information.\n',
            'OCR':'The answer should conduct an Optical Character Recognition (OCR) analysis on the content asked about. Just answer the question with a single word or phrase if possible. No irrelevant information should be included.\n',
            'Entity Recognition':'The answer should  contain recognition results of entities mentioned in the question. Just answer the question with a single word or phrase if possible. No irrelevant information should be included.\n',
            'Spatial Awareness':"The answer should be based on the spatial relationships between entities in the qusition. It is best to provide corresponding evidence for all judgments. If specific numerical answers are not present in the image but can be estimated based on its content, the estimated results can be used. Just provide the answer in one word or a short sentence. No irrelevant information should be included.\n",
            'Numerical Calculation':'You should perform mathematical calculations based on the information in the image. You need to estimate some values that do not display directly in the image for answering the question. You should show the calculation process and output the calculated result.\n',
            'Accurate Numerical Calculation':'You should perform mathematical calculations based on the information in the image. You need to provide a step-by-step calculation and obtain a numerical result.\n',
            'Financial Knowledge':'The answer should be based on financial knowledge. Briefly answer the question within100 words. The answer should not contain irrelevant content related to the picture.\n',
            'Risk Warning':'You should warn investment risk based on the information in the chart and professional financial knowledge. All your arguments need to be supported by facts or theories and the answer should fall within 150 words.\n',
            'Investment Advice':'You should provide investment advice based on the information in the chart and professional financial knowledge. All your arguments need to be supported by facts or theories and the answer should fall within 150 words.\n',
            'Explain Reason':'You should provide explanation based on the information in the chart and professional financial knowledge. All your arguments need to be supported by facts or theories and the answer should fall within 150 words.\n',
            'Not Applicable':'If you cannot answer, please say "Not Applicable", and provide the explainations.',
        }
        prompt += format_prompt[line['task_category']] if line['task_category'] in format_prompt else ''
        if not pd.isna(line['background']):
            prompt += 'This is background: '
            prompt += line['background']

        msgs = []
        if isinstance(tgt_path, list):
            msgs.extend([dict(type='image', value=p) for p in tgt_path])
        else:
            msgs = [dict(type='image', value=tgt_path)]
        msgs.append(dict(type='text', value=prompt))
        return msgs
    
    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.mmfin import MMfin_auxeval, MMfin_acc
        suffix = eval_file.split('.')[-1]
        model = judge_kwargs['model']
        storage = eval_file.replace(f'.{suffix}', f'_{model}.xlsx')
        tmp_file = eval_file.replace(f'.{suffix}', f'_{model}.pkl')
        nproc = judge_kwargs.pop('nproc', 4)
        if not osp.exists(storage):
            data = load(eval_file)
            model = build_judge(max_tokens=3, **judge_kwargs)
            assert model.working(), ('MMfin evaluation requires a working OPENAI API\n' + DEBUG_MESSAGE)

            lt = len(data)
            lines = [data.iloc[i] for i in range(lt)]
            tups = [(model, line) for line in lines]
            indices = [line['index'] for line in lines]

            ans = load(tmp_file) if osp.exists(tmp_file) else {}
            tups = [x for x, i in zip(tups, indices) if i not in ans]
            indices = [i for i in indices if i not in ans]

            if len(indices):
                new_results = track_progress_rich(
                    MMfin_auxeval,
                    tups,
                    nproc=nproc,
                    chunksize=nproc,
                    keys=indices,
                    save=tmp_file,
                )
                ans = load(tmp_file)
                for k, v in zip(indices, new_results):
                    assert k in ans
                    assert ans[k]['log'] == v['log'] and ans[k]['score'] == v['score']
            data['score'] = [ans[idx]['score'] for idx in data['index']]
            data['log'] = [ans[idx]['log'] for idx in data['index']]
            dump(data, storage)

        score, score2, score3, total_score = MMfin_acc(storage)
        score_pth = storage.replace('.xlsx', '_score_task_category.csv')
        score_pth2 = storage.replace('.xlsx', '_score_image_type.csv')
        score_pth3 = storage.replace('.xlsx', '_score_image_style.csv')

        dump(score, score_pth)
        dump(score2, score_pth2)
        dump(score3, score_pth3)
        return total_score

class MMfin_CN(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'MMfin_CN': 'https://opencompass.openxlab.space/utils/VLMEval/MMfin_CN.tsv'
    }
    DATASET_MD5 = {'MMfin_CN': '748aa6d4aa9d4de798306a63718455e3'}
 
    def build_prompt(self, line):
        if isinstance(line, int):
            line = self.data.iloc[line]

        tgt_path = line['image_path']
        root = LMUDataRoot()
        tgt_path = osp.join(root, 'images/MMfin_CN', tgt_path)

        prompt = '你是一位精通各种金融图表且拥有广泛金融知识的金融专家。现在给你一张图像和相应的问题。请回答这个问题。'
        prompt += '/n这是问题：'
        prompt += line['question']
        prompt += '/n这是答案的一些要求：'
        format_prompt = {
            'Image Caption':'以整体-部分结构描述此图像。先以一句话概括图像的主要主题。如果图像描述多个对象，首先用一句话介绍每个对象，如果对象之间存在一些联系，用一句话解释每个联系。如果对象很复杂，可以进一步解释。你的回答应少于 250 个字，且不应包含任何无关信息。\n',
            'OCR':'答案应对所询问的内容进行光学字符识别分析。如果可能，仅用一个单词或短语回答问题。不应包含无关信息。\n',
            'Entity Recognition':'答案应包含问题中提到的实体的识别结果。如果可能，仅用一个单词或短语回答问题。不应包含无关信息。\n',
            'Spatial Awareness':'答案应基于问题中实体之间的空间关系。最好为所有判断提供相应证据。如果图像中没有特定的数值答案，但可以根据其内容进行估计，则可以使用估计结果。仅用一个单词或简短的句子提供答案。不应包含无关信息。\n',
            'Numerical Calculation':'你应根据图像中的信息进行数学计算。你需要估计一些未在图像中直接显示的值以回答问题。你应展示计算过程并输出计算结果。\n',
            'Accurate Numerical Calculation':'你应根据图像中的信息进行数学计算。你需要提供逐步计算过程并获得一个数值结果。\n',
            'Financial Knowledge':'答案应基于金融知识。在 100 字内简要回答问题。答案不应包含与图片无关的内容。\n',
            'Risk Warning':'你应根据图表中的信息和专业金融知识警告投资风险。你的所有论点都需要有事实或理论支持，答案应在 150 字以内。\n',
            'Investment Advice':'你应根据图表中的信息和专业金融知识提供投资建议。你的所有论点都需要有事实或理论支持，答案应在 150 字以内。\n',
            'Explain Reason':'你应根据图表中的信息和专业金融知识提供原因解释。你的所有论点都需要有事实或理论支持，答案应在 150 字以内。\n',
            'Not Applicable':'如果你无法回答，请说“无法回答”，并提供解释。',
        }
        prompt += format_prompt[line['task_category']] if line['task_category'] in format_prompt else ''
        if not pd.isna(line['background']):
            prompt += '这是背景：'
            prompt += line['background']

        msgs = []
        if isinstance(tgt_path, list):
            msgs.extend([dict(type='image', value=p) for p in tgt_path])
        else:
            msgs = [dict(type='image', value=tgt_path)]
        msgs.append(dict(type='text', value=prompt))
        return msgs
    
    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.mmfin import MMfin_CN_auxeval, MMfin_acc
        suffix = eval_file.split('.')[-1]
        model = judge_kwargs['model']
        storage = eval_file.replace(f'.{suffix}', f'_{model}.xlsx')
        tmp_file = eval_file.replace(f'.{suffix}', f'_{model}.pkl')
        nproc = judge_kwargs.pop('nproc', 4)
        if not osp.exists(storage):
            data = load(eval_file)
            model = build_judge(max_tokens=3, **judge_kwargs)
            assert model.working(), ('MMfin_CN evaluation requires a working OPENAI API\n' + DEBUG_MESSAGE)

            lt = len(data)
            lines = [data.iloc[i] for i in range(lt)]
            tups = [(model, line) for line in lines]
            indices = [line['index'] for line in lines]

            ans = load(tmp_file) if osp.exists(tmp_file) else {}
            tups = [x for x, i in zip(tups, indices) if i not in ans]
            indices = [i for i in indices if i not in ans]

            if len(indices):
                new_results = track_progress_rich(
                    MMfin_CN_auxeval,
                    tups,
                    nproc=nproc,
                    chunksize=nproc,
                    keys=indices,
                    save=tmp_file,
                )
                ans = load(tmp_file)
                for k, v in zip(indices, new_results):
                    assert k in ans
                    assert ans[k]['log'] == v['log'] and ans[k]['score'] == v['score']
            data['score'] = [ans[idx]['score'] for idx in data['index']]
            data['log'] = [ans[idx]['log'] for idx in data['index']]
            dump(data, storage)

        score, score2, score3, total_score = MMfin_acc(storage)
        score_pth = storage.replace('.xlsx', '_score_task_category.csv')
        score_pth2 = storage.replace('.xlsx', '_score_image_type.csv')
        score_pth3 = storage.replace('.xlsx', '_score_image_style.csv')

        dump(score, score_pth)
        dump(score2, score_pth2)
        dump(score3, score_pth3)
        return total_score

class MMfin_Binary(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'MMfin_Binary': 'https://opencompass.openxlab.space/utils/VLMEval/MMfin_Binary.tsv'
    }
    DATASET_MD5 = {'MMfin_Binary': '748aa6d4aa9d4de798306a63718455e3'}
    def load_data(self, dataset):
        data_path = osp.join(LMUDataRoot(), f'{dataset}.tsv')

        if file_size(data_path, 'GB') > 1:
            local_path = data_path.replace('.tsv', '_local.tsv')
            if not osp.exists(local_path) or os.environ.get('FORCE_LOCAL', None):
                from ..tools import LOCALIZE

                LOCALIZE(data_path, local_path)
            data_path = local_path
        return load(data_path)

    def evaluate(self, eval_file, **judge_kwargs):
        suffix = eval_file.split('.')[-1]
        score_pth = eval_file.replace(f'.{suffix}', '_score.csv')
        df = pd.read_excel(eval_file)
        y_true_l = df['answer']  # 真实答案
        y_pred_l = df['prediction']  # 模型预测  
        out = []
        total = len(df)
        correct = 0
        tp = 0
        fp = 0
        fn = 0
        for i in range(total):
            y_pred = y_pred_l[i].strip("。")
            y_true = y_true_l[i].strip("。")
            if y_pred == y_true:
                correct+=1
            if y_pred == "是":
                if y_true == "是":
                    tp += 1
                else:
                    fp += 1
            elif y_pred == "否":
                if y_true == "是":
                    fn += 1
        # out.append(d
        acc = correct / total if total > 0 else 0
        f1 = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) > 0 else 0
        score = {
        "ACC": acc,
        "F1": f1,}
        score_df = pd.DataFrame([score])
        dump(score_df, score_pth)
        return score






class MTVQADataset(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {'MTVQA_TEST': 'https://opencompass.openxlab.space/utils/VLMEval/MTVQA_TEST.tsv'}
    DATASET_MD5 = {'MTVQA_TEST': 'd87c17dbab934b7cd89c0a3c1c5657f4'}

    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        data = load(eval_file)
        assert 'answer' in data and 'prediction' in data and 'category' in data
        data['prediction'] = [str(x) for x in data['prediction']]
        data['answer'] = [str(x) for x in data['answer']]
        if 'split' in data:
            assert np.all([x.lower() == 'test' for x in data['split']]), 'We only support MTVQA_TEST for now. '
        lt = len(data)
        category_scores = defaultdict(list)
        for i in range(lt):
            line = data.iloc[i]
            ans = line['answer'].strip().lower().replace('.', '')
            pred = line['prediction'].strip().lower().replace('.', '')
            cate = line['category']
            score = 1.0 if ans in pred else 0.0
            category_scores[cate].append(score)
            category_scores['Average'].append(score)
        # Calculate the average score for each category, the score is normalized to [0, 100]
        category_averages = {category: np.mean(scores) * 100 for category, scores in category_scores.items()}

        suffix = eval_file.split('.')[-1]
        result_file = eval_file.replace(f'.{suffix}', '_acc.json')
        dump(category_averages, result_file)

        return category_averages

    # MT-VQA adopts a custom prompt
    def build_prompt(self, line):
        msgs = super().build_prompt(line)
        assert sum([x['type'] == 'text' for x in msgs]) == 1
        for item in msgs:
            if item['type'] == 'text':
                item['value'] += '\nAnswer the question using a word or phrase in the language of the question.'
        return msgs


class TableVQABench(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'TableVQABench': 'https://pai-aigc-photog.oss-cn-hangzhou.aliyuncs.com/mentor-vil/datasets/tablevqa-bench.tsv'
    }
    DATASET_MD5 = {'TableVQABench': '2550adc61bdc82d8e62f3b003de7c62d'}

    from .utils.tablevqabench import FINTABNETQA_PROMPT, VTABFACT_PROMPT, VWTQ_PROMPT

    # It returns a DataFrame
    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        import pandas as pd
        from .utils.tablevqabench import evaluate_fintabnet, evaluate_tabfact, evaluate_wtq

        data = load(eval_file)
        assert 'answer' in data and 'prediction' in data

        data['prediction'] = data['prediction'].str.replace('^Answer: ', '', regex=True)
        data_group = dict(tuple(data.groupby('split')))
        eval_result = {'split': [], 'average_scores': []}
        for split in ['fintabnetqa', 'vtabfact', 'vwtq', 'vwtq_syn']:
            data_split = data_group[split].to_dict(orient='records')
            if split == 'fintabnetqa':
                split_eval_meta = evaluate_fintabnet(data_split, ['accuracy'])
            elif split == 'vtabfact':
                split_eval_meta = evaluate_tabfact(data_split, ['accuracy'])
            elif split == 'vwtq' or split == 'vwtq_syn':
                split_eval_meta = evaluate_wtq(data_split, ['accuracy'])
            eval_result['split'].append(split)
            eval_result['average_scores'].append(split_eval_meta['average_scores'])

        suffix = eval_file.split('.')[-1]
        result_file = eval_file.replace(f'.{suffix}', '_acc.csv')
        eval_result = pd.DataFrame(eval_result)
        dump(eval_result, result_file)

        return eval_result

    # TableVQABench adopts a custom prompt
    def build_prompt(self, line):
        msgs = super().build_prompt(line)
        assert sum([x['type'] == 'text' for x in msgs]) == 1
        for item in msgs:
            if item['type'] == 'text':
                if line['split'] == 'fintabnetqa':
                    item['value'] = self.FINTABNETQA_PROMPT.format_map({'question': item['value']})
                elif line['split'] == 'vtabfact':
                    item['value'] = self.VTABFACT_PROMPT.format_map({'question': item['value']})
                elif line['split'] == 'vwtq_syn' or line['split'] == 'vwtq':
                    item['value'] = self.VWTQ_PROMPT.format_map({'question': item['value']})
        return msgs


class CustomVQADataset(ImageBaseDataset):
    TYPE = 'VQA'

    def load_data(self, dataset):
        data_path = osp.join(LMUDataRoot(), f'{dataset}.tsv')

        if file_size(data_path, 'GB') > 1:
            local_path = data_path.replace('.tsv', '_local.tsv')
            if not osp.exists(local_path) or os.environ.get('FORCE_LOCAL', None):
                from ..tools import LOCALIZE

                LOCALIZE(data_path, local_path)
            data_path = local_path
        return load(data_path)

    def evaluate(self, eval_file, **judge_kwargs):
        raise NotImplementedError


class CRPE(ImageBaseDataset):
    TYPE = 'VQA'
    DATASET_URL = {
        'CRPE_EXIST': 'https://huggingface.co/datasets/petter12321/crpe_vlmevalkit/resolve/main/CRPE_EXIST.tsv',
        'CRPE_RELATION': 'https://huggingface.co/datasets/petter12321/crpe_vlmevalkit/resolve/main/CRPE_RELATION.tsv'
    }
    DATASET_MD5 = {
        'CRPE_EXIST': '315584e23ac1ff7f8719ed3b7ad90f08',
        'CRPE_RELATION': 'bad7094cde0b572288f4b119c2d0c656'}

    @classmethod
    def evaluate(self, eval_file, **judge_kwargs):
        from .utils.crpe import is_correct
        # find-image, count-text, find-text,
        # infer-choose, count-image, visual-reasoning
        score = {
            'exist': 0,
            'subject': 0,
            'predicate': 0,
            'object': 0,
            'total': 0,
        }
        num = {
            'exist': 0,
            'subject': 0,
            'predicate': 0,
            'object': 0,
            'total': 0,
        }
        final_score_dict = {
            'exist': 0,
            'subject': 0,
            'predicate': 0,
            'object': 0,
            'total': 0,
        }
        data = load(eval_file)
        lt = len(data)
        lines = [data.iloc[i] for i in range(lt)]
        for i in tqdm(range(len(lines))):
            line = lines[i]
            predict = str(line['prediction'])
            answers = str(line['answer'])
            # print("predict =", predict)
            # print("answers =", answers)
            category = line['category']
            if is_correct(answers, predict):
                score[category] += 1
                score['total'] += 1
            num[category] += 1
            num['total'] += 1

        for category in ['exist', 'subject', 'predicate', 'object', 'total']:
            if num[category] != 0:
                final_score_dict[category] = score[category] / num[category]
            else:
                final_score_dict[category] = None

        score_pth = eval_file.replace('.xlsx', '_score.json')
        dump(final_score_dict, score_pth)
        return final_score_dict

    def build_prompt(self, line):
        ROOT = LMUDataRoot()
        msgs = super().build_prompt(line)
        for msg in msgs:
            if msg['type'] == 'image':
                msg['value'] = osp.join(osp.join(ROOT, 'images', self.dataset_name), msg['value'])
        return msgs
