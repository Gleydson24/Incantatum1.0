import mediapipe
import os

print("\n--- RELATÓRIO DE DEBUG ---")
print(f"Onde o Python acha que o mediapipe está: {mediapipe.__file__}")
print(f"O que tem dentro do mediapipe: {dir(mediapipe)}")

try:
    print(f"Tentando acessar solutions: {mediapipe.solutions}")
    print("Sucesso: solutions encontrado!")
except AttributeError:
    print("ERRO: solutions NÃO encontrado.")

print("\nVerificando arquivos na pasta atual que podem atrapalhar:")
arquivos = os.listdir('.')
if 'mediapipe.py' in arquivos:
    print("!!! PERIGO !!! Existe um arquivo 'mediapipe.py' nesta pasta. DELETE ELE.")
else:
    print("Nenhum arquivo 'mediapipe.py' na raiz. (Isso é bom)")