from setuptools import setup, find_packages

setup(
    name='asyffmpeg',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiofiles',
        'ffprobe',
        # Додайте інші залежності, які необхідні для вашого пакету
    ],
    author='drhspfn',
    author_email='jenya.gsta@gmail.com',
    description='A library for asynchronous operation with FFmpeg, providing the ability to track events such as start, end, and encoding progress.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/drhspfn/asyffmpeg',
    classifiers=[
        'Programming Language :: Python :: 3',
        'ffmpeg'
    ],
)
