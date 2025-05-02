from setuptools import setup, find_packages

setup(
    name="gvmaker",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "ttkbootstrap==1.10.1",
        "opencv-python-headless==4.8.1.78",
        "pillow==10.1.0",
        "numpy==1.26.2",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "pyautogui==0.9.54",
        "screeninfo==0.8.1",
        "pynput==1.7.6",
        "keyboard==0.13.5",
        "moviepy==1.0.3",
        "sounddevice==0.4.6",
        "soundfile==0.12.1",
        "pyinstaller==6.1.0",
        "pywin32>=305"
    ],
    entry_points={
        "console_scripts": [
            "gvmaker=src.main:main",
        ],
    },
    author="Berk Karaduman",
    author_email="berk.karaduman@example.com",
    description="A simple and efficient screen recorder",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/karadumann/gvmaker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 