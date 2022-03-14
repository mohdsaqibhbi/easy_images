from setuptools import setup, find_packages
import sys

with open('README.md', encoding='utf-8') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='easy_images_downloader',
    version='0.0.5',
    description='Download hundreds of images from Google. Do image post processing later.',
    long_description=README,
	long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    author='Mohd Saqib',
    author_email='mohdsaqibhbi@gmail.com',
    keywords=['easy images', 'easy images downloader', 'python image download', 'google images', 'download images', 'image downloader'],
    url='https://github.com/mohdsaqibhbi/easy_images.git',
    download_url='https://pypi.org/project/easy_images_downloader/'
)
osin_install_requires = ['requests', 'opencv-python', 'beautifulsoup4', 'selenium',
                                'tqdm', 'webdriver-manager', 'tabulate']

install_requires = osin_install_requires + ([
                    "python-magic-bin"] if sys.platform.startswith("win") else [
                    'python-magic'])

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
