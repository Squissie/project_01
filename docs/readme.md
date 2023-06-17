## CovidVisionX

A website-based tool for machine learning assisted X-ray image classification

Features:
- allows both local installation and web hosting
- separate accounts for nurses, doctors and administrators
- patient data grouping into consultations
- implements pre-trained Support Vector Machine and Convolutional Neural Network machine learning models
- categorizes x-ray images into Covid-19, Pneumonia, or No detectable sickness
- for Covid-19, categorizes the sickness severity

Example website [hosted with Heroku](https://covidvisionx.herokuapp.com)

---

### Local installation

Due to size constraints, the example website only supports the SVM model. It's easy to install a locally hosted version though, with the CNN model and severity detection.

1. Install Python 3.9+
2. Optionally, create a virtual environment for this app to separate its modules from your main python installation
3. Install the required modules using `python pip install -r requirements.txt`
4. Run the app using `python manage.py runserver`

---

### Other

The [reset script](/reset_database.py) reverts the local app's database file to the original state, with only testing users.

The Machine Learning repository for all machine learning models used and tested in this project can be found at [COVIDVisionX ML Repository](https://github.com/nazkl/COVIDVisionX_ML)
