from PIL import Image, ImageDraw

# Create a 256x256 image with a transparent background
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a circle
circle_color = (52, 152, 219)  # Blue color
draw.ellipse([20, 20, size-20, size-20], fill=circle_color)

# Draw a camera symbol
camera_color = (255, 255, 255)  # White color
# Camera body
draw.rectangle([60, 80, size-60, size-80], fill=camera_color)
# Camera top
draw.rectangle([80, 60, size-80, 80], fill=camera_color)
# Lens
draw.ellipse([80, 100, size-80, size-100], fill=(0, 0, 0))

# Save as ICO file
image.save('icon.ico', format='ICO') 