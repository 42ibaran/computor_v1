# Computor v1

## Functionality
The program solves polynomial equations of degrees less than 3.

Program supports equations in free form. You can:
* Omit coefficients before X
* Omit X for free coefficients
* Omit multiplication sign
* Omit degree of X
* Omit ^ sign

## Usage with Python
```
python computor.py [@h] [@i] [@p precision] equation
```
The project was tested with python >3.7. Might work with other versions but who knows.

## Usage with Docker
If you don't have python installed, today is your lucky day my friend. Just use Docker to build the image and then run the program in a container like so:
```
docker build -t computor .
docker run --rm computor "X^2-1=0"
```

## Bonuses:
* Support of free form
* Repeating degrees
* Output precision parameter [@p precision]
* Result as complex numbers for D<0 [@i]
* Dockerfile

For more information refer to the [subject](https://cdn.intra.42.fr/pdf/pdf/13223/en.subject.pdf)
