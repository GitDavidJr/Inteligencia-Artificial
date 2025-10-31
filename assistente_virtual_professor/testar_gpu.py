import torch

if __name__ == "__main__":
    dispositivo = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"dispositivo utilizado: {"GPU" if dispositivo == "cuda:0" else dispositivo}")