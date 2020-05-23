from setuptools import setup

setup(
    name='baselinesme',
    packages=['baselinesme'],
    version='0.1',
    install_requires=[
        'cloudpickle==0.5.2',
        'numpy',
        'pandas',
        'psutil',
        'scipy',
        'tensorflow==1.15.2',
        'Flask',
        'joblib',
        'baselines',
    ],
    entry_points={
        'console_scripts': [
            'run_policy=baselinesme.load_policy:main'
        ]
    }
)
