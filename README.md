# Easy Images

This repo contains the Python script that can let you download the images from Google for the given keyword. Also, there are some additional functionalities added that can help in post-image processing.

Preparing the image dataset which is not publicly available, is still a challenging task. Machine Learning Engineers need image data when building something of a Computer Vision. But due to the non-availability of the data, they are left with nothing but 2 choices - either to drop the idea or postpone it until some data is available. And manually downloading the images from Google could take forever.

With this Python script, you can easily download hundreds of images from Google within a couple of minutes and try out your Computer Vision idea. You can also remove duplicate images while downloading or later.

## Features
- Download hundreds of images within couple of minutes with one go.
- Remove duplicate images while downloading.
- Provide the summary of the download.
- Remove duplicate images (later) irrespective of the image size or resolution.
- Resize all the images in a directory.
- Convert all the images in a directory, into grayscale.
- Calculate average image size of all the images in a directory.
- Run above 3 post processing operations just in one go.

## Getting Started

### Prerequisites
Require Python >= 3.8

### Installation

#### Using Github repo
1. Clone the [repo](https://github.com/mohdsaqibhbi/easy_images) using `git clone https://github.com/mohdsaqibhbi/easy_images.git`.
2. Install the dependencies by running `pip3 install -r requirements.txt`.

#### Using pip
`pip3 install easy-images-downloader`

### Usage
- To download images from Google.

```
from easy_images.easy_images import EasyImages

keywords = "dogs, cats, horse"

easy_response = EasyImages()
easy_response.download(keywords=keywords, max_limit=100)
```

- Post processing on all the images in a directory, e.g removing duplicates images.

```
from easy_images.easy_images import EasyImages

image_dir = "easy_images/dogs"

easy_response = EasyImages()
easy_response.post_processing(image_dir=image_dir, remove_duplicates=True)
```

### Parameters

- **Class initialization**

    ```easy_response = EasyImages(browser_name="chrome", headless=True, loading_timeout=2)```

    - ***browser_name*** : *(str), {"chrome", "brave"}, default="chrome"*

        The browser to use.
    - ***headless*** : *(boolean), default=True*

        While downloading, whether to open browser or not. Set headless=False to open browser.
    - ***loading_timeout*** : *(float), default=2*

        Page loading timeout. Less for fast and more for slow internet.

- **Download images**

    ```easy_response.download(keywords, output_dir="easy_images", max_limit=10, image_formats={".jpg", ".jpeg", ".png"}, remove_duplicates=False)```

    - ***keywords*** : *(str / dict), e.g. "dogs, cats" or {"dogs": 100, "cats": 200}, default=Required*

        Keywords for which images will be downloaded.
    - ***output_dir*** : *(str), default="easy_images"*

        Output directory where images will be downloaded for each keyword.
    - ***max_limit*** : *(int), default=10*

        Maximum number of images to download.
    - ***image_formats*** : *(set), default={".jpg", ".jpeg", ".png"}*

        To download fast but slighty low resolution images. Set quick=False for slighty high resolution images. When quick=False, the average downloading time for 100 images is approximately 6 mins.
    - ***remove_duplicates*** : *(boolean), default=False*

        Whether to remove duplicate images or not while downloading. Set remove_duplicates=True to remove duplicates.

- **Post processing on images**

    ```easy_response.post_processing(image_dir, remove_duplicates=False, resize=None, grayscale=False, avg_image_size=False)```

    - ***image_dir*** : *(str), e.g. "easy_images/dogs", default=Required*

        Directory name from where duplicate images need to be removed.
    - ***remove_duplicates*** : *(boolean), default=False*

        Whether to remove duplicate images from a directory. Set remove_duplicates=True to remove.
    - ***resize*** : *(tuple), e.g (200 x 200), default=None*

        Image size to resize. If resize is equal to tuple of int, resize the images.
    - ***grayscale*** : *(boolean), default=False*

        Whether to convert images in a directory,  into grayscale. Set grayscale=True to convert.
    - ***avg_image_size*** : *(boolean), default=False*

        Whether to calculate average image size of all the images in a directory. Set avg_image_size=True to calculate.

## Limitations

**Note: This script/package Will not work in Colab.**

This scripts download the images with size approximately 200 x 200. This is because Google allows to download the images with rendered size only. Only few images can be downloaded with original image size. The original urls of the image are encrypted and with the encryption, image size is changed to a particular size which is lesser than the original image size.

Please share your ideas to overcome these limitations. Let's together build a beautiful python script that can help lots of people.

## Next Steps
Following the next steps to improve the script:
- Find a method to download the images with original size.
- Build the script without selenium for fast downloading. Selenium is a bit slower.
- Add image similarity factor so that more relevant images can be downloaded.
- Optimize the overall script with additional functionalities for faster downloading of images.
- Add some more generic OpenCV functionalities. Please share you ideas if you got some.

**Everyone is welcome to contribute to this script. If you want to contribute please write me on [Linkedin](https://www.linkedin.com/in/mohdsaqibhbi) or [Email](mohdsaqibhbi@gmail.com) me.**

## Disclaimer
This Python script allows you to download hundreds of Google images. Please do not download or use any image whose copyright has been violated. Google indexes images and makes them searchable. It does not create its own images, and as a result, none of them are protected by copyright. The original creator of the image owns the copyrights.

## LICENSE
This project is licensed under the terms of the [MIT license](LICENSE).

## Follow me

- Follow me on Linkedin: [mohdsaqibhbi](https://www.linkedin.com/in/mohdsaqibhbi)
- Subscribe my Youtube channel: [StarrAI](https://www.youtube.com/channel/UCooZBjTCrnM3LH1nIqAmDQA)
