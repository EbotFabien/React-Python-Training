class Rectangle:
    def __init__(self,length ,width):
        self.__length=length
        self.__width = width

    def get_area(self):
        return self.__length * self.__width
    
    def get_perimeter(self):
        return 2 * (self.__length + self.__width)
    
rectangle = Rectangle(5,4)
print(rectangle.get_area(),rectangle.get_perimeter())