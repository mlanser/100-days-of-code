from math import factorial as f

print('='.center(60, '='))
print("= Let's try a few things ...")
print('='.center(60, '='))
print("\n\nFirst a loop ...")
y = 0
for i in range(10):
    x = (i+1) * 10
    y = y+x
    print(x)

print("\n... then printing out some sum ...")
print(y) 


print("\n... then some math using factorials ...")
fruits=10
fruitsPerBasket=3
baskets=f(fruits) // (f(fruitsPerBasket) * f(fruits - fruitsPerBasket))

print("How hany baskets of fruit can we fill if we have the following?")
print("Fruits: " + str(fruits))
print("Fruits per basket: " + str(fruitsPerBasket))
print("Answer: " + str(baskets) + " baskets\n\n")


print('='.center(60, '='))
print("= Let's play with strings and other stuff ...")
print('='.center(60, '='))

s = "This is a long string!"
print("4th char of '" + s + "' is: " + s[3])
print("4th word of '" + s + "' is: " + s.split()[3] + "\n\n")

print('='.center(60, '='))
print("= Finally print what we all came here to see ...")
print('='.center(60, '='))
print("\n" + "--> Hello World! <--".center(60, ' ') + "\n\n")