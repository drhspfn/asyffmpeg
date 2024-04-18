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
    # description='короткий_опис_пакету',
    # long_description=open('README.md').read(),
    # long_description_content_type='text/markdown',
    # url='посилання_на_репозиторій_проекту',
    classifiers=[
        'Programming Language :: Python :: 3',
        'ffmpeg'
    ],
)
