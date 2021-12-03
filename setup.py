from setuptools import setup

setup(
    name='mkdocs-image-gen',
    version='0.0.1',
    packages=['image_gen'],
    url='',
    license='',
    author='David Ritter',
    author_email='',
    description='Image Generator',
    install_requires=['mkdocs', 'pandas', 'svgwrite'],
    entry_points={
        'mkdocs.plugins': [
            'replace = replace:ReplacePlugin',
        ]
    },
)
