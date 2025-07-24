'''
len()
msg.title()
msg.upper()
msg.lower()
msg.find()
msg.replace('','')
'....' in msg
2 ** 2 = 4
2 + 2 = 4
3 - 2 = 1
10 // 3 = 3
10 / 3 = 3.33333
10 % 3 = 1
round(2.9) = 3
abs(-2.9) = 2.9
import math
math.floor
     ceil
     ....
     is_good_credit = False
price = 1000000
if is_good_credit: 
    down_payment = price * 0.1
   
    
else:
    down_payment = price * 0.2

print(f"they need put down: ${down_payment}")
has_good_income = True
hes_good_salary = False

if has_good_income or hes_good_salary:
    print('give him downfucking payment')
and, or, not and
name = "f has_good_income or hes_good_salary: give him downfucking payment and, or, not and"

if len(name) < 3:
      print('it is short')
elif len(name) >= 50:
      print('it is too long')
else :
      print('it looks good')
weight = input ('Weight: ')
question = input ('(K)g or (L)bs :')

if question == 'k':
    print(int(weight) * 2.20)
elif question == 'l':
    print(int(weight) * 0.49)
else:
    print('try again')
i = 1
while i <= 5:
     print('*' * i)
     i = i + 1
print('qutardi blet soxun gotunuze')

i = 1
y = 9


while i <= 3:
    secret_num = input('Guess:' )
    if int(secret_num) == y:
        print('you won')
        break
    else:
        print('you lost')
    i = i + 1
print('game finished')

command = ""
started = False
stopped = False
  
while True:
     command = input('> ').lower()
     if command == 'start':
          if started:
               print('Car alrady started ')
          else :
               started = True
               print("get car to started: ")
     elif command == 'stop':
          if stopped:
               print('Car already stopped agilli ol')
          else :
               stopped = True
               print("car is stopping rn... ")
     elif command == 'help':
          print(
       or starting car write start
for stopping car write stop
                for quitting game write quit
                )
     elif command == 'quit':
          break
     else:
           print("I don't understand what is that " )

prices = [10, 20, 30]
cem = 0
for price in prices:
    cem += price
    print(f"cem: {cem}")

numbers = [1, 1, 1, 4]
for x_count in numbers:
    output = ''
    for count in range(x_count):
        output += 'x'
    print(output)

ededler =[1, 2, 5, 3444 ,3, 15, 6, 8]
max = ededler[0]

for eded in ededler:
    if eded > max:
        max = eded
print (max)

matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]


]
for row in matrix:
    for item in row:
        print(f"{item[0]}")

 numbers= [2, 4, 5, 8, 12, 3, 45]
numbers.insert(1, 31)
print(numbers)  


umbers = [2, 4, 5, 6, 2]
dublic = []

for number in  numbers:
    if number not in dublic:
        dublic.append(number)

print(dublic)

tele = (1, 3, 2)
x, y, z = tele
print(y)


telefon = input("telefon :")

digit_mappin = {
    "0" : "IBO",
    "1" : "one",
    "2" : "two",
    "3" : "three",
    "4" : "four",
    "5" : "five",
    "6" : "six",
    "7" : "seven"
}

output = ""

for ch in telefon:
    output += digit_mappin.get(ch, "oops!") + " "

print(output)







def ibo_pro(firs_name, last_name):
     print(f'Hi baby {firs_name} {last_name}!')
     print("auye jizn varam")


print ("start")
ibo_pro("Turan", "hasanzade")
print("finish")

def sahe_cevre(radius):
    return radius * 3 / 2 * 3.14 *radius

cavab = sahe_cevre(3)
print(cavab)



def emoji_coverter(mesaj):
    sozler = mesaj.split(' ')
    emojis = {
    ":)" : "❤️",
    "):" : "😭"
     }
    output = " "
    for soz in sozler:
     output += emojis.get(soz, soz) + " "
    return output

mesaj = input (">")
print(emoji_coverter(mesaj))


try: 
    month = int(input("ayin_sayi: "))
    income = 20000
    gelir = income/month
    print(gelir)
except ZeroDivisionError:
    print('Age cannot be 0.')
except ValueError: 
    print('invalid error')

umbers 
strings 
boolens
---
lists 
dictionaries


class Point:
    def draw(self):
        print('draw')
    def urey(self):
        print('ikiminbasi')


point1 = Point()
point1.x = 10
point1.y = 20
print(point1.x)
point1.urey()  

point2 = Point()
point2.x = 1
print(point2.x)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def draw(self):
        print('draw')
    def urey(self):
        print('agilli')


point = Point(10, 20)
print(point.y)


class Person:
    def __init__(self, name ):
        self.name = name
    def talk(self):
        print(f'Salam necesiz homretli {self.name}')

person = Person('Fikrat bey')
person.talk()

insan = Person('Ulviyye hasanov')
insan.talk()



class Ana:
    def walk(self):
        print('walk')


class Dog(Ana):
    pass

class Cat(Ana):
    def miaw(self):
        print('miyaw')

heyvan = Cat()
heyvan.miaw()

from utils import find_max

result = find_max()

'''













