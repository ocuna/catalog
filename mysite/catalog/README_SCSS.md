Sass is required to convert this file into css: https://sass-lang.com/install

Keep in mind that catalog\assets\scss\demo_boostrap_vars contains both \_mixins.scss, \_variables.scss which need replaced to match the path of whatever boostrap-compatible theme you are using.  These files are based on a modified bootstrap 4.1 build.

REPLACE below to match your build:
```sh
cd $ROOT:\to\your\django\catalog\assets\scss
sass --watch dmf_catalog.scss:../../static/dmf_catalog/css/dmf_catalog.style.css
```

Change your scss and then run the following to update or compile your scss make it work:
```sh
cd $ROOT:\to\your\django>
python manage.py collectstatic
```