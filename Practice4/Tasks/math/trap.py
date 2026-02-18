def trapezoid(height, first1, first2):
    return ((first1+first2)*height)/2

Height=int(input("Height: "))
base1=int(input("Base, first value: "))
base2=int(input("Base, second value: "))
area=trapezoid(Height, base1, base2)
print("Expected Output: ",area)