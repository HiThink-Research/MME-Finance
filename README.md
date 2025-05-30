<p align="center">
  <h1 align="center">
    <img src="static/logo.png" alt="BizFinBench logo" height="40" style="position:relative; top:6px;">
  MME-Finance: A Multimodal Finance Benchmark for Expert-level Understanding and Reasoning</h1>
    <p align="center">
    <strong>Ziliang Gan</strong>
    ,
    <strong>Dong Zhang</strong>
    ,
    <strong>Haohan Li</strong>
    ,
    <strong>Yang Wu</strong>
    ,
    <strong>Ji Liu</strong>
    ,
     <strong>Haipang Wu</strong>
    ,
     <strong>Chaoyou Fu</strong>
    ,
     <strong>Zenglin Xu</strong>
    ,
    <br>
     <strong>Rongjunchen Zhang</strong><sup>♠</sup>,
     <strong>Yong Dai</strong>
  </p>
  <div class="is-size-5 publication-authors" align="center">
        <span class="author-block">
            <sup>♠</sup>Corresponding author, zhangrongjunchen@myhexin.com
        </span>
    </div>
    <br>
  📖<a href="https://arxiv.org/abs/2411.03314">Paper</a> |🏠<a href="https://hithink-research.github.io/MME-Finance/">Homepage</a></h3>|🤗<a href="https://huggingface.co/datasets/hithink-ai/MME-Finance">Huggingface</a></h3>
<div align="center"></div>
<p align="center">
  <p>
In recent years, multimodal benchmarks for general domains have guided the rapid development of multimodal models on general tasks. However, the financial field has its peculiarities. It features unique graphical images (e.g., candlestick charts, technical indicator charts) and possesses a wealth of specialized financial knowledge (e.g., futures, turnover rate).
    
Benchmarks from general fields often fail to measure the performance of multimodal models in the financial domain, and thus cannot effectively guide the rapid development of large financial models. To promote the development of large financial multimodal models, we introduce <strong>MME-Finance</strong>, the first comprehensive bilingual multimodal benchmark designed for financial analysis. 

## 📢 News 
- 🚀 [05/30/2025] We released <strong>MME-Finance-MT</strong> multi-turn question benchmark and <strong>MME-Finance-Binary</strong> benchmark.
- 🚀 [01/08/2025] <strong><a href="https://huggingface.co/datasets/hithink-ai/MME-Finance">We have released all samples in both English and Chinese.</a></strong>
- 🚀 [11/05/2024] We released <strong>MME-Finance</strong> benchmark, a bilingual multimodal benchmark in financial domain.

## 💡 Highlights
- 🔥 <strong>Bilingual multimodal financial benchmark:</strong> MME-Finance is the first Bilingual multimodal financial benchmark which comprises 1,171 English and 1,103 Chinese open-ended questions, covering diverse financial image types and various multimodal capabilities. 
- 🔥 <strong>Evaluation strategy: </strong> MME-Finance proposes a Elaborate evaluation strategy that taking image into consideration, and has a high consistency with humans. It can serve as a reference for evaluating MLLMs for other works.
- 🔥 <strong>Valuable insights: </strong>We conduct extensive evaluation on 19 MLLMs based on MME-Finance, revealing critical insights about the strengths and shortcomings of the current MLLMs in financial applications.

[下载/查看PDF文件](Supplementary_pdf_ACMMM.pdf)

## 🛠️ Usage

<!-- ### Judgement -->
We have integrated MMfin into the VLMEvalKit framework. For the environment configuration and the use of API, please refer to [VLMEvalKit](https://github.com/open-compass/VLMEvalKit).
Regarding the data, first of all, you should download the `MMfin.tsv` and `MMfin_CN.tsv` files, as well as the relevant financial images. The folder structure is shown as follows:
```
├─ datasets
    ├─ images
        ├─ MMfin
            ...
        ├─ MMfin_CN
            ...
        ├─ MMfin_MT_CN
            ...      
        ├─ MMfin_Binary
            ...      
    │ MMfin.tsv
    │ MMfin_CN.tsv
    | MMfin_MT_CN.tsv
    | MMfin_Binary.tsv

```
The following is the process of inference and evaluation (Qwen2-VL-2B-Instruct as an example):
```
export LMUData="The path of the datasets"
python run.py --data MMfin --model Qwen2-VL-2B-Instruct --verbose
python run.py --data MMfin_CN --model Qwen2-VL-2B-Instruct --verbose
python run.py --data MMfin_MT_CN --model Qwen2-VL-2B-Instruct --verbose
python run.py --data MMfin_Binary --model Qwen2-VL-2B-Instruct --verbose
```
## Results
###  Evaluation results on the English MME-Finance for all tasks.
| Model | Overall | Image Caption | OCR | Entity Recognition | Spatial Awareness | Accurate Numerical Calculation | Estimated Numerical Calculation | Risking Warning | Investment Advice | Reason Explanation | Financial Question Answer | Not Applicable |
|-------|---------|---------------|-----|--------------------|------------------|-------------------------------|-------------------------------|----------------|------------------|-------------------|--------------------------|---------------|
| **Open source MLLMs** | 
| Yi-VL-34B | 17.57 | 29.39 | 1.46 | 3.93 | 8.73 | 5.56 | 11.43 | 42.73 | 35.09 | 58.89 | 47.48 | 36.36 |
| CogVLM2-19B | 46.32 | 67.32 | 61.24 | 35.83 | 16.59 | 44.51 | 33.33 | 59.09 | 52.83 | 31.11 | 58.64 | 93.64 |
| InternVL2-2B | 37.42 | 59.63 | 46.97 | 21.23 | 18.52 | 28.27 | 19.05 | 59.09 | 50.94 | 60.00 | 51.70 | 33.63 |
| InternVL2-4B | 47.69 | 67.44 | 58.88 | 33.74 | 18.95 | 55.49 | 30.48 | 68.18 | 54.34 | 64.44 | 60.95 | 59.09 |
| InternVL2-8B | 53.58 | 71.71 | 68.43 | 38.28 | 25.33 | 62.86 | 37.14 | 72.73 | 60.75 | 76.67 | 63.13 | 61.82 |
| InternVL2-76B | 61.62 | 83.17 | 77.64 | 47.60 | 30.31 | 70.08 | 41.90 | 75.45 | 66.42 | 76.67 | 72.24 | 79.09 |
| InternVL3-2B | 53.07 | 71.22 | 73.48 | 41.84 | 28.91 | 60.15 | 31.43 | 57.27 | 51.32 | 67.78 | 53.74 | 69.09 |
| InternVL3-8B | 65.69 | 74.39 | 84.27 | 60.00 | 44.63 | 76.99 | 43.33 | 65.45 | 56.60 | 73.33 | 69.53 | 76.36 |
| InternVL3-9B | 65.89 | 77.93 | 84.72 | 60.74 | 43.84 | 75.34 | 40.48 | 69.09 | 56.98 | 70.00 | 70.34 | 68.18 |
| InternVL3-14B | 69.02 | 79.51 | 84.72 | 64.05 | 49.52 | 80.90 | 46.19 | 66.36 | 57.36 | 71.11 | 72.24 | 82.73 |
| InternVL3-38B | 67.75 | 79.51 | 86.07 | 56.81 | 46.29 | 82.11 | 47.14 | 69.09 | 56.98 | 74.44 | 70.88 | 87.27 |
| InternVL3-78B | 71.24 | 79.51 | 89.66 | 62.45 | 49.61 | **88.27** | 49.05 | 75.45 | 58.49 | 74.44 | 74.97 | 89.09 |
| LLaMA3.2-11B | 42.51 | 62.44 | 39.10 | 32.02 | 14.50 | 55.79 | 37.14 | 60.00 | 50.57 | 68.89 | 57.55 | 61.82 |
| LLaMA3.2-90B | 48.76 | 64.27 | 46.74 | 41.27 | 25.85 | 55.64 | 22.86 | 63.64 | 61.13 | 64.44 | 65.58 | 81.82 |
| LLaVA-Next-7B | 28.18 | 58.41 | 22.81 | 14.85 | 11.09 | 7.07 | 10.00 | 45.45 | 47.55 | 12.22 | 54.97 | 55.45 |
| LLaVA-Next-13B | 31.37 | 62.68 | 25.39 | 22.58 | 10.31 | 12.63 | 9.05 | 47.27 | 40.00 | 12.22 | 59.46 | 78.18 |
| MiniCPM2.6 | 51.65 | 71.22 | 63.71 | 37.67 | 24.37 | 55.64 | 21.43 | 72.73 | 58.87 | 66.67 | 66.80 | 77.27 |
| Phi3-Vision | 46.69 | 69.88 | 57.64 | 28.34 | 18.08 | 47.52 | 34.76 | 65.45 | 58.11 | 68.89 | 57.41 | 100.0 |
| Phi3.5-Vision | 38.99 | 67.56 | 33.03 | 18.90 | 20.52 | 32.33 | 19.52 | 67.27 | 55.85 | 72.22 | 54.42 | 93.64 |
| Qwen2VL-2B | 44.42 | 62.07 | 66.07 | 28.47 | 20.09 | 44.36 | 23.33 | 53.63 | 44.53 | 58.89 | 53.47 | 68.18 |
| Qwen2VL-7B | 44.44 | 62.19 | 64.49 | 26.50 | 19.04 | 45.56 | 27.62 | 57.27 | 48.30 | 58.89 | 54.97 | 68.18 |
| Qwen2VL-72B | 65.69 | 82.56 | 87.52 | 55.46 | 27.16 | 83.76 | 40.95 | 78.18 | 65.66 | 77.78 | 75.37 | 90.91 |
| Qwen2.5VL-3B | 57.85 | 63.54 | 82.47 | 49.08 | 30.83 | 70.53 | 46.67 | 61.82 | 52.83 | 68.89 | 60.14 | 90.91 |
| Qwen2.5VL-7B | 62.00 | 72.93 | 82.47 | 49.08 | 30.83 | 70.53 | 46.67 | 61.82 | 52.83 | 68.89 | 60.14 | 90.91 |
| Qwen2.5VL-32B | 65.41 | 75.61 | 86.29 | 49.33 | 42.79 | 81.95 | 45.71 | 71.82 | 59.24 | 70.00 | 69.93 | 87.27 |
| Qwen2.5VL-72B | 68.20 | 75.73 | 87.64 | 61.60 | 40.00 | 84.21 | 58.09 | 72.73 | 58.49 | 72.22 | 75.37 | 87.27 |
| **Proprietary MLLMs** |
| Gemini1.5Pro | 61.84 | 82.20 | 80.22 | 48.59 | 23.14 | 78.20 | 50.95 | 76.36 | 69.43 | 75.56 | 70.75 | 80.91 |
| Claude3.5-Sonnet | 63.91 | 87.80 | 63.70 | 54.23 | 35.46 | 72.33 | 60.00 | **80.91** | **72.83** | **82.22** | 73.33 | 95.45 |
| GPT-4o-mini | 64.43 | 86.46 | 73.71 | 54.72 | 34.93 | 69.17 | 56.19 | 76.36 | 63.46 | 72.22 | 77.55 | 87.27 |
| GPT-4o | 72.79 | 89.88 | 86.18 | 61.60 | 45.68 | 82.41 | **65.24** | **80.91** | 70.57 | 80.00 | **82.59** | 84.55 |
| Gemini2.5Pro | **79.28** | **90.85** | **94.61** | **70.18** | **63.14** | 87.97 | **65.24** | 75.45 | 68.68 | 78.89 | 80.54 | **100.00** |

### Evaluation results on English MME-Finance for different types and styles of images. 
| Candlestick chart | Technical indicator chart | Statistical chart | Table | Document | Mixed chart | Computer Screenshot | Mobile Photograph | Vertical Screenshot on Mobile | Horizontal Screenshot on Mobile |  
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |  
| **Open source MLLMs** |  
| Yi-VL-34B | 23.64 | 16.36 | 18.76 | 15.42 | 14.89 | 32.38 | 19.42 | 14.39 | 26.06 | 16.62 |  
| CogVLM2-19B | 39.44 | 35.57 | 52.30 | 50.38 | 45.76 | 57.14 | 47.33 | 44.22 | 49.70 | 49.09 |  
| InternVL2-2B | 30.35 | 33.18 | 38.62 | 40.00 | 38.49 | 58.10 | 40.36 | 34.73 | 35.45 | 34.55 |  
| InternVL2-4B | 35.38 | 38.98 | 51.48 | 54.66 | 47.77 | 63.81 | 50.87 | 44.85 | 43.64 | 45.71 |  
| InternVL2-8B | 42.38 | 45.00 | 60.41 | 57.79 | 52.59 | 67.62 | 56.39 | 51.56 | 48.79 | 49.87 |  
| InternVL2-76B | 55.52 | 47.50 | 63.02 | 70.84 | 63.09 | 67.62 | 62.78 | 61.73 | 54.54 | 58.70 |  
| InternVL3-2B | 38.32 | 47.16 | 58.42 | 57.86 | 53.53 | 62.86 | 55.09 | 52.19 | 46.97 | 49.09 |  
| InternVL3-8B | 53.29 | 60.91 | 70.65 | 71.30 | 64.75 | 63.81 | 68.88 | 63.80 | 56.97 | 61.82 |  
| InternVL3-9B | 52.87 | 60.00 | 71.48 | 72.21 | 64.39 | 67.62 | 69.06 | 63.59 | 57.88 | 64.16 |  
| InternVL3-14B | 59.44 | 61.59 | 73.06 | 77.25 | 67.27 | 60.95 | 70.76 | 67.89 | 62.12 | 69.35 |  
| InternVL3-38B | 61.12 | 64.32 | 68.52 | 76.26 | 65.18 | 59.05 | 69.35 | 65.86 | 60.30 | 74.29 |  
| InternVL3-78B | 64.90 | 64.32 | 70.65 | 78.32 | 73.53 | 61.90 | 72.96 | 69.45 | 63.33 | 76.62 |  
| LLaMA3.2-11B | 35.24 | 31.59 | 47.63 | 50.92 | 39.42 | 48.57 | 45.16 | 39.07 | 38.79 | 47.79 |  
| LLaMA3.2-90B | 40.56 | 40.11 | 51.20 | 58.17 | 45.83 | 64.76 | 50.14 | 46.33 | 46.06 | 56.10 |  
| LLaVA-Next-7B | 29.65 | 23.52 | 28.80 | 28.32 | 28.34 | 44.76 | 28.45 | 26.08 | 32.73 | 35.32 |  
| LLaVA-Next-13B | 27.27 | 26.36 | 33.68 | 32.14 | 32.95 | 39.05 | 32.67 | 29.20 | 30.91 | 35.84 |  
| MiniCPM2.6 | 45.03 | 45.00 | 54.23 | 58.63 | 49.42 | 59.05 | 52.09 | 50.51 | 45.45 | 60.78 |  
| Phi3-Vision | 37.62 | 40.00 | 49.48 | 49.54 | 48.71 | 62.86 | 49.75 | 43.08 | 40.30 | 52.21 |  
| Phi3.5-Vision | 32.73 | 30.45 | 46.25 | 38.24 | 39.21 | 59.05 | 44.73 | 32.28 | 41.52 | 36.88 |  
| Qwen2VL-2B | 38.74 | 40.80 | 46.60 | 46.26 | 44.68 | 57.14 | 45.13 | 43.71 | 38.79 | 48.57 |  
| Qwen2VL-7B | 39.72 | 41.70 | 46.60 | 46.11 | 44.03 | 54.29 | 44.73 | 44.09 | 36.97 | 50.91 |  
| Qwen2VL-72B | 60.12 | 60.11 | 65.15 | 71.73 | 66.04 | 74.24 | 67.65 | 62.78 | 68.48 | 67.01 |  
| Qwen2.5VL-3B | 50.07 | 54.32 | 61.79 | 62.14 | 55.68 | 60.95 | 61.05 | 54.81 | 49.39 | 60.78 |  
| Qwen2.5VL-7B | 55.24 | 57.61 | 64.95 | 66.64 | 60.79 | 61.90 | 62.53 | 61.14 | 60.30 | 64.94 |  
| Qwen2.5VL-32B | 60.98 | 59.77 | 67.70 | 72.44 | 62.37 | 63.81 | 67.40 | 63.25 | 60.00 | 69.09 |  
| Qwen2.5VL-72B | 62.38 | 58.86 | 69.76 | 77.02 | 67.48 | 63.81 | 70.54 | 66.08 | 57.88 | 73.25 |  
| **Proprietary MLLMs** |  
| GeminiPro1.5 | 51.19 | 57.39 | 65.09 | 69.24 | 58.92 | 73.33 | 64.91 | 58.31 | 56.67 | 65.97 |  
| Claude3.5-Sonnet | 51.47 | 53.52 | 72.51 | 71.15 | 59.93 | **79.05** | 67.47 | 58.19 | 69.70 | 68.57 |  
| GPT-4o-mini | 58.18 | 55.80 | 70.38 | 66.56 | 64.03 | 76.00 | 66.44 | 60.89 | 63.94 | 72.21 |  
| GPT-4o | 67.27 | 70.45 | 75.19 | 75.11 | 72.16 | 76.19 | 76.06 | 66.84 | **74.85** | 84.16 |  
| Gemini2.5Pro | **72.73** | **71.82** | **82.61** | **85.80** | **78.13** | 74.29 | **81.08** | **76.92** | 74.24 | **85.19** |  
### Evaluation results on the Chinese MME-Finance for all tasks.
| Model | Overall | Image Caption | OCR | Entity Recognition | Spatial Awareness | Accurate Numerical Calculation | Estimated Numerical Calculation | Risking Warning | Investment Advice | Reason Explanation | Financial Question Answer | Not Applicable |
|-------|---------|---------------|-----|--------------------|------------------|-------------------------------|-------------------------------|----------------|------------------|-------------------|--------------------------|---------------|
| **Open source MLLMs** |
| Yi-VL-34B | 23.50 | 43.89 | 0.66 | 9.86 | 4.94 | 23.97 | 18.13 | 20.00 | 28.79 | 60.00 | 51.81 | **100.0** |
| CogVLM2-19B | 35.32 | 55.69 | 41.10 | 37.84 | 16.02 | 39.37 | 29.38 | 8.11 | 31.43 | 26.15 | 28.47 | 85.00 |
| InternVL2-2B | 50.06 | 68.06 | 68.57 | 45.68 | 24.94 | 45.56 | 39.38 | 59.46 | 47.25 | 67.69 | 51.39 | 13.00 |
| InternVL2-4B | 45.78 | 67.22 | 60.22 | 43.51 | 19.28 | 51.43 | 38.75 | 31.89 | 46.59 | 63.08 | 36.94 | 47.00 |
| InternVL2-8B | 58.44 | 73.47 | 76.92 | 55.14 | 25.18 | 52.84 | 42.50 | 53.51 | 61.32 | 76.92 | 67.78 | 60.00 |
| InternVL2-76B | 62.63 | 73.47 | 75.71 | 61.35 | 38.43 | 64.13 | 53.13 | 58.38 | 63.08 | 75.38 | 67.36 | 45.00 |
| InternVL3-2B | 50.06 | 68.06 | 68.57 | 45.68 | 24.94 | 45.56 | 39.38 | 59.46 | 47.25 | 67.69 | 51.39 | 13.00 |
| InternVL3-8B | 69.21 | 75.83 | 86.81 | 68.65 | 36.87 | 74.92 | 63.13 | 77.30 | 68.57 | 81.54 | 73.06 | 60.00 |
| InternVL3-9B | 69.12 | 75.69 | 85.38 | 68.78 | 39.64 | 75.24 | 61.25 | 70.81 | 70.11 | 83.08 | 74.44 | 40.00 |
| InternVL3-14B | 71.91 | 76.39 | 90.55 | 65.27 | 49.28 | 79.37 | 68.13 | 67.57 | 67.69 | 84.62 | 74.03 | 70.00 |
| InternVL3-38B | 74.07 | 76.25 | 90.88 | 75.54 | 48.43 | 81.43 | 70.63 | 77.84 | 68.35 | 84.62 | **78.06** | 50.00 |
| InternVL3-78B | 73.62 | 74.17 | 91.87 | 69.59 | 48.80 | 82.38 | 78.13 | 80.00 | 67.25 | 75.38 | 77.50 | 65.00 |
| LLaVA-Next-7B | 21.45 | 50.69 | 8.35 | 12.16 | 9.28 | 16.03 | 13.13 | 12.43 | 28.35 | 46.15 | 25.14 | 90.00 |
| LLaVA-Next-13B | 19.87 | 49.58 | 8.68 | 12.30 | 13.01 | 14.60 | 9.38 | 8.11 | 24.84 | 13.85 | 17.64 | 90.00 |
| MiniCPM2.6 | 38.60 | 53.47 | 64.29 | 45.27 | 23.98 | 18.41 | 27.50 | 32.43 | 36.70 | 35.38 | 27.92 | 14.00 |
| Phi3-Vision | 31.91 | 57.92 | 32.31 | 40.68 | 16.02 | 29.05 | 23.13 | 22.70 | 32.31 | 43.08 | 14.31 | 75.00 |
| Yi-VL-34B | 17.57 | 29.39 | 1.46  | 3.93 | 8.73 | 5.56 | 11.43 | 42.73 | 35.09 | 58.89 | 47.48 | 36.36 |
| Phi3.5-Vision [15] | 30.12 | 55.97 | 19.45 | 20.27 | 23.85 | 20.48 | 24.38 | 28.65 | 41.98 | 41.54 | 26.94 | **100.0** |
| Qwen2VL-2B [16] | 49.12 | 65.97 | 63.41 | 48.38 | 24.94 | 39.05 | 36.88 | 36.76 | 46.37 | 56.92 | 51.53 | **100.0** |
| Qwen2VL-7B [16] | 64.91 | 73.61 | 84.95 | 64.05 | 34.34 | 69.68 | 58.13 | 55.14 | 59.34 | 67.69 | 65.97 | 95.00 |
| Qwen2VL-72B [16] | 73.35 | 79.58 | 89.67 | 73.24 | 55.90 | 73.81 | 73.13 | 69.19 | 65.05 | 76.92 | 74.17 | 60.00 |
| Qwen2.5VL-3B [8] | 61.38 | 72.22 | 78.68 | 55.41 | 39.64 | 65.08 | 58.13 | 51.35 | 55.38 | 75.38 | 60.56 | 75.00 |
| Qwen2.5VL-7B [8] | 69.94 | 75.56 | 88.68 | 67.84 | 49.40 | 73.02 | 71.25 | 64.86 | 64.62 | 73.85 | 67.08 | 75.00 |
| Qwen2.5VL-32B [8] | 70.43 | 76.53 | 86.48 | 70.27 | 48.19 | 72.06 | 62.50 | 80.00 | 65.93 | **90.77** | 68.06 | 75.00 |
| Qwen2.5VL-72B [8] | 76.95 | 78.33 | 94.73 | 75.54 | 54.46 | 81.11 | 73.13 | **83.78** | 70.99 | 84.62 | 77.92 | 85.00 |
| **Proprietary MLLMs** |
| Claude3.5-Sonnet [18] | 71.04 | 74.03 | 74.73 | 77.43 | 51.33 | 76.83 | 66.25 | 79.46 | 68.79 | 81.54 | 70.28 | 97.00 |
| GeminiPro1.5 [17] | 69.25 | 75.42 | 81.43 | 67.30 | 44.58 | 76.03 | 78.75 | 74.59 | 62.42 | 66.15 | 74.58 | 60.00 |
| GPT-4o-mini [6] | 54.58 | 66.25 | 59.01 | 47.84 | 30.60 | 50.63 | 54.38 | 63.78 | 58.68 | 72.31 | 67.36 | 65.00 |
| GPT-4o [6] | 59.53 | 69.86 | 68.90 | 58.92 | 39.04 | 57.46 | 55.63 | 60.54 | 53.19 | 63.08 | 68.19 | 56.00 |
| Gemini2.5Pro [5] | **81.07** | 76.11 | **96.04** | **85.41** | **67.23** | **86.98** | **87.88** | **83.78** | **72.09** | 87.69 | 77.08 | 75.00 |

### Evaluation results on Chinese MME-Finance for different types and styles of images. 
| Candlestick chart | Technical indicator chart | Statistical chart | Table | Document | Mixed chart | Computer Screenshot | Mobile Photograph | Vertical Screenshot on Mobile | Horizontal Screenshot on Mobile |  
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |  
| **Open source MLLMs** |  
| Yi-VL-34B | 26.00 | 21.66 | 22.87 | 23.55 | 23.63 | 24.52 | 26.30 | 20.49 | 25.09 | 22.22 |  
| CogVLM2-19B | 38.86 | 33.59 | 31.19 | 37.74 | 37.48 | 37.48 | 37.11 | 32.50 | 36.77 | 39.17 |  
| InternVL2-2B | 36.29 | 35.80 | 39.01 | 37.90 | 48.22 | 32.26 | 43.70 | 36.92 | 39.63 | 34.72 |  
| InternVL2-4B | 34.43 | 44.20 | 46.93 | 48.31 | 51.56 | 37.10 | 51.90 | 40.80 | 43.72 | 45.56 |  
| InternVL2-8B | 49.71 | 55.69 | 56.44 | 59.60 | 66.44 | 53.23 | 61.80 | 55.31 | 62.11 | 50.00 |  
| InternVL2-76B | 55.86 | 64.75 | 61.39 | 62.74 | 67.56 | 53.87 | 65.55 | 57.28 | 69.44 | 63.61 |  
| InternVL3-2B | 35.86 | 53.15 | 49.80 | 47.02 | 58.81 | 48.06 | 52.04 | 47.77 | 52.92 | 46.39 |  
| InternVL3-8B | 63.43 | 67.40 | 73.07 | 68.15 | 72.59 | 64.52 | 72.04 | 65.27 | 72.80 | 69.17 |  
| InternVL3-9B | 60.29 | 65.08 | 70.50 | 73.71 | 72.59 | 62.90 | 73.22 | 66.03 | 69.81 | 62.78 |  
| InternVL3-14B | 60.14 | 69.94 | 74.16 | 76.94 | 75.41 | 61.61 | 75.12 | 68.08 | 73.66 | 73.06 |  
| InternVL3-38B | 61.43 | 73.48 | 76.73 | 79.11 | 76.07 | 66.77 | 77.49 | 71.12 | 75.16 | 70.00 |  
| InternVL3-78B | 64.14 | 72.38 | 77.92 | 76.61 | 74.89 | 67.10 | 77.30 | 70.00 | 73.42 | 75.00 |  
| LLaVA-Next-7B | 29.57 | 20.88 | 20.00 | 16.21 | 25.33 | 13.55 | 22.89 | 19.42 | 23.23 | 21.67 |  
| LLaVA-Next-13B | 24.14 | 21.66 | 21.39 | 16.37 | 19.56 | 15.48 | 20.33 | 19.29 | 19.88 | 20.83 |  
| MiniCPM2.6 | 36.57 | 36.69 | 37.92 | 40.08 | 44.81 | 18.06 | 38.58 | 35.80 | 47.33 | 36.67 |  
| Phi3-Vision | 31.71 | 35.47 | 29.21 | 31.45 | 34.30 | 22.26 | 36.45 | 27.32 | 31.55 | 34.72 |  
| Phi3.5-Vision | 30.29 | 35.03 | 27.92 | 25.48 | 33.33 | 27.10 | 32.09 | 27.54 | 29.81 | 35.28 |  
| Qwen2VL-2B | 40.71 | 42.10 | 49.11 | 49.68 | 59.41 | 41.61 | 49.95 | 48.88 | 51.80 | 39.72 |  
| Qwen2VL-7B | 55.71 | 60.55 | 69.21 | 66.13 | 68.37 | 64.52 | 69.29 | 62.41 | 62.73 | 59.72 |  
| Qwen2VL-72B | 64.14 | 71.71 | 77.52 | 75.65 | 75.26 | 67.74 | 76.35 | 69.96 | 74.53 | 74.17 |  
| Qwen2.5VL-3B | 44.14 | 59.34 | 63.37 | 65.16 | 67.78 | 56.77 | 64.08 | 61.61 | 56.40 | 55.28 |  
| Qwen2.5VL-7B | 60.57 | 65.86 | 72.38 | 72.50 | 74.15 | 66.45 | 73.51 | 69.42 | 66.83 | 59.17 |  
| Qwen2.5VL-32B | 64.00 | 72.82 | 68.32 | 68.15 | 77.48 | 63.23 | 73.70 | 67.37 | 70.56 | 70.00 |  
| Qwen2.5VL-72B | 60.00 | 77.90 | 79.90 | 81.21 | **80.96** | 68.39 | 80.95 | 74.11 | 78.14 | 68.61 |  
| **Proprietary MLLMs** |  
| Claude3.5-Sonnet | 68.71 | 71.27 | 72.28 | 71.13 | 72.22 | 66.13 | 73.22 | 64.46 | 80.12 | 78.89 |  
| GeminiPro1.5 | 66.43 | 73.04 | 73.76 | 63.15 | 71.78 | 63.23 | 72.23 | 64.51 | 74.16 | 70.28 |  
| GPT-4o-mini | 55.71 | 67.96 | 58.22 | 43.55 | 56.89 | 35.16 | 55.40 | 45.63 | 70.68 | 69.44 |  
| GPT-4o | 53.14 | 71.93 | 62.97 | 52.98 | 62.59 | 39.35 | 64.03 | 47.01 | 75.90 | 74.44 |  
| Gemini2.5Pro | **73.48** | **82.87** | **84.65** | **83.31** | 80.74 | **73.87** | **82.93** | **78.48** | **83.48** | **80.83** | 
### Evaluation results on True/Fasle version of MME-Finance.

| Model | Accuracy | F1-Score |
|-------|----------|----------|
| **Open source MLLMs** |
| InternVL3-2B  | 68.45 | 77.88 |
| InternVL3-8B  | 75.00 | 81.05 |
| InternVL3-9B | 68.95 | 78.43 |
| InternVL3-14B  | 71.10 | 79.92 |
| InternVL3-38B  | 76.90 | 83.31 |
| InternVL3-78B | 81.30 | 86.26 |
| Qwen2.5VL-3B  | 69.85 | 79.33 |
| Qwen2.5VL-7B  | 83.90 | 87.14 |
| Qwen2.5VL-32B  | 78.60 | 84.47 |
| Qwen2.5VL-72B  | 85.40 | 88.73 |
| **Proprietary MLLMs** |
| Claude3.5-Sonnet  | 82.40 | 86.94 |
| GPT-4o-mini  | 69.10 | 72.26 |
| GPT-4o  | **87.95** | **90.31** |
| Gemini2.5Pro | 83.50 | 87.56 |

### Evaluation results on multi-turn version of MME-Finance. 


| Model | Creativity | Richness | Visual Perception | Logical Coherence | Answer | Average Accuracy | Image Relationship Understanding |
|-------|------------|----------|-------------------|--------------------|--------|------------------|-------------------------------|
| **Open source MLLMs** |
| InternVL3-2B  | 59.66 | 69.90 | 68.70 | 79.90 | 76.46 | 70.46 | 70.84 |
| InternVL3-8B  | 62.26 | 70.12 | 71.43 | 83.63 | 79.94 | 73.99 | 73.56 |
| InternVL3-9B  | 69.31 | 77.65 | 77.06 | 87.17 | 85.53 | 79.52 | 79.37 |
| InternVL3-14B  | 54.35 | 62.77 | 65.46 | 79.29 | 75.46 | 67.00 | 67.39 |
| InternVL3-38B  | 62.45 | 70.82 | 71.36 | 83.88 | 81.34 | 73.82 | 73.94 |
| InternVL3-78B  | 71.01 | 77.78 | 77.40 | 87.51 | 85.85 | 79.73 | 79.88 |
| Qwen2.5VL-3B  | 45.41 | 56.74 | 59.47 | 72.34 | 68.02 | 60.53 | 60.42 |
| Qwen2.5VL-7B  | 72.83 | 81.07 | 80.40 | 89.25 | 88.49 | 83.29 | 82.55 |
| Qwen2.5VL-32B  | 76.53 | 79.94 | 75.44 | 82.50 | 81.76 | 78.21 | 79.07 |
| Qwen2.5VL-72B  | 75.81 | 82.96 | **81.53** | **90.25** | **89.58** | **84.26** | 84.06 |
| **Proprietary MLLMs** |
| Claude3.5-Sonnet  | 82.10 | 86.37 | 78.99 | 90.21 | 89.08 | 81.80 | 84.76 |
| GPT-4o-mini  | 59.01 | 63.72 | 45.44 | 73.66 | 63.28 | 46.74 | 58.64 |
| GPT-4o | 63.50 | 69.79 | 58.83 | 80.23 | 72.85 | 61.74 | 67.82 |
| Gemini2.5Pro | **84.59** | **87.15** | 80.69 | 90.08 | 87.69 | 84.07 | **85.71**|





## ✒️Citation
```
@article{gan2024woodpecker,
  title={MME-Finance: A Multimodal Finance Benchmark for Expert-level Understanding and Reasoning},
  author={Gan, Ziliang and Lu, Yu and Zang, Dong and Li, Haohan and Liu, Che and Liu, Jian and Liu, Ji and Wu, Haipang and Fu, Chaoyou and Xu, Zenglin and Zhang, Rongjunchen and Dai, Yong},
  journal={arXiv preprint arXiv:2411.03314},
  year={2024}
}
```

## 📄 License
![Code License](https://img.shields.io/badge/Code%20License-Apache_2.0-green.svg) ![Data License](https://img.shields.io/badge/Data%20License-CC%20By%20NC%204.0-red.svg) **Usage and License Notices**: The data and code are intended and licensed for research use only.
License: Attribution-NonCommercial 4.0 International It should abide by the policy of OpenAI: https://openai.com/policies/terms-of-use

## 💖 Acknowledgement
* <a href="https://github.com/open-compass/VLMEvalKit"><u>VLMEvalKit</u></a>: the codebase we built upon. 
