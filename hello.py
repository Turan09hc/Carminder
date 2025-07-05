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
  
'''

