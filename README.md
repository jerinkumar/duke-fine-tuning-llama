# Supervised Fine-tuning of Small Language Models using DUKE-based Model Distillation

## Fine-tune Meta's lightweight Llama small language models using document understanding and knowledge extraction (DUKE) for model distillation

This project uses a novel technique I've coined, DUKE (Document Understanding and Knowledge Extraction), along with LoRA (Low-Rank Adaptation), specifically, Rank-Stabilized LoRA (rsLoRA), a supervised fine-tuning technique and a method within PEFT (Parameter-Efficient Fine-Tuning), to fine-tune Meta Llama 3.2 3B Instruct, a lightweight 3 billion parameter instruction-tuned generative model. We will fine-tune the Llama model on an entirely new domain, similar to the trade show example.

### Web Scraper

Create a virtual Python environment on Mac/Linux

```sh
python --version # I am using Python 3.13.2

python -m pip install virtualenv -Uqqq
python -m venv .venv
source .venv/bin/activate
```

Install Python package dependencies

```sh
python -m pip install pip -Uqqq
python -m pip install -r requirements.txt -Uqqq
```

Deactivate and delete virtual environment once you are done

```sh
deactivate
rm -rf .venv
```

### Jupyter Notebook

Tested with a NVIDIA-based GPU with a minimum of 12-16 GBs of VRAM.
