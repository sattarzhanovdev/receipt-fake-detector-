from PIL import Image, ImageFilter, ImageStat


def detect_tampering(image: Image.Image) -> list[str]:
    risks: list[str] = []
    width, height = image.size

    if width < 400 or height < 400:
        risks.append("низкое разрешение изображения")

    grayscale = image.convert("L")
    sharpness = ImageStat.Stat(grayscale.filter(ImageFilter.FIND_EDGES)).mean[0]
    if sharpness < 3:
        risks.append("изображение слишком размыто")

    brightness = ImageStat.Stat(grayscale).mean[0]
    if brightness < 35 or brightness > 252:
        risks.append("подозрительная яркость изображения")

    return risks
