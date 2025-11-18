from setuptools import setup
import versioneer

#Dependancy lists maintained here and in tox.ini
sp_install_requires = [
  'requests==2.31.0',
  'pytz==2025.2',
  'python-dateutil==2.9.0.post0'
]
sp_tests_require = [
  'nose==1.3.7',
  'python_Testing_Utilities==0.1.11'
]

all_require = sp_install_requires + sp_tests_require

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='PythonAPIClientBase',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Base classes for APIClients',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/rmetcalf9/PythonAPIClientBase',
      author='Robert Metcalf',
      author_email='rmetcalf9@googlemail.com',
      license='MIT',
      packages=['PythonAPIClientBase'],
      zip_safe=False,
      install_requires=sp_install_requires,
      tests_require=sp_tests_require,
      include_package_data=True)
