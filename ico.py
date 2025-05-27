from PIL import Image
import sys

# Набор из 70 ASCII-символов от темного к светлому
gscale1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def resize_image(image, new_width=100):
    """
    Изменение размера изображения с учетом соотношения сторон символов.
    """
    width, height = image.size
    ratio = height / width
    factor = 0.5  # Корректировка для соотношения сторон символов (2:1)
    new_height = int(ratio * new_width * factor)
    if new_height == 0:
        new_height = 1
    return image.resize((new_width, new_height), Image.NEAREST)

def grayscaler(image):
    """
    Преобразование изображения в оттенки серого.
    """
    return image.convert("L")

def pixels_to_ascii(image):
    """
    Преобразование пикселей в ASCII-символы.
    """
    pixels = image.getdata()
    ascii_str = ""
    len_gscale = len(gscale1)
    for pixel in pixels:
        i = (pixel * len_gscale) // 256
        if i >= len_gscale:
            i = len_gscale - 1
        ascii_str += gscale1[i]
    return ascii_str

def main(image_path, new_width=100):
    """
    Основная функция для обработки изображения и вывода ASCII-арта.
    """
    try:
        image = Image.open(image_path)
    except IOError:
        print(f"Не удалось открыть {image_path}")
        return

    resized_image = resize_image(image, new_width)
    grayscale_image = grayscaler(resized_image)
    ascii_str = pixels_to_ascii(grayscale_image)
    pixels_per_row = resized_image.width
    ascii_image = "\n".join([ascii_str[i:i+pixels_per_row] for i in range(0, len(ascii_str), pixels_per_row)])
    print(ascii_image)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python ascii_art.py <путь_к_изображению> [ширина]")
        sys.exit(1)
    image_path = sys.argv[1]
    new_width = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    main(image_path, new_width)