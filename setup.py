from setuptools import setup, find_packages

setup(
    name="mmprofiler",
    version="0.1.0",
    author="Сметанка Володимир",
    author_email="your.email@example.com",
    description="Легкий Python-пакет для мультимодального профайлінгу датасетів (текст, зображення, аудіо, табличні дані).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VladzioG/mmprofiler.git",  
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3",
        "Pillow>=9.0"
    ],
    entry_points={
        "console_scripts": [
            "mmprofiler=mmprofiler.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
