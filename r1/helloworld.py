from math import factorial as f

print("Let's try a few things ...")
print("\nFirst a loop ...")
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
print("Answer: " + str(baskets) + " baskets")


print("\n... and finally print what we all came here to see ...")
print("\n--> Hello World! <--\n\n")