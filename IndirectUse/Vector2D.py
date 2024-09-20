class Vector2D:
    """A two-dimensional vector with Cartesian coordinates."""

    def __init__(self, x = 0, y = 0, polar = False, degrees = False):

            self.x = x
            self.y = y

            if isinstance(x, (Vector2D, list, tuple)) and not y: 
                self.x = x[0]
                self.y = x[1]
            
            if degrees:
                y = math.radians(y)

            if polar:
                self.x = x * math.cos(y)
                self.y = x * math.sin(y)

            self.length = self.__abs__()
            self.angle = math.atan2(self.y, self.x)

    def __str__(self):
        """Human-readable string representation of the vector."""
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def __repr__(self):
        """Unambiguous string representation of the vector."""
        return repr((self.x, self.y))

    def dot(self, other):
        """The scalar (dot) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector2D):
            raise TypeError('Can only take dot product of two Vector2D objects')
        return self.x * other.x + self.y * other.y
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = dot

    def cross(self, other):
        """The vector (cross) product of self and other. Both must be vectors."""

        if not isinstance(other, Vector2D):
            raise TypeError('Can only take cross product of two Vector2D objects')
        return abs(self) * abs(other) * math.sin(self-other)
    # Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
    __matmul__ = cross

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        """Vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        """Recursive vector addition."""
        return Vector2D(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """Multiplication of a vector by a scalar."""

        if isinstance(scalar, int) or isinstance(scalar, float):
            return Vector2D(self.x*scalar, self.y*scalar)
        raise NotImplementedError('Can only multiply Vector2D by a scalar')

    def __rmul__(self, scalar):
        """Reflected multiplication so vector * scalar also works."""
        return self.__mul__(scalar)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return Vector2D(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector2D(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        """One way to implement modulus operation: for each component."""
        return Vector2D(self.x % scalar, self.y % scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)

    def __round__(self, decimals):
        """Round the vector2D x and y"""
        return Vector2D(round(self.x, decimals), round(self.y, decimals))

    def __iter__(self):
        """Return the iterable object"""
        for i in [self.x, self.y]:
            yield i

    def __getitem__(self, index):
        """Return the iterable object"""
        if index == 0 or index == 'x':
            return self.x
        elif index == 1 or index == 'y':
            return self.y
        raise NotImplementedError('Vector2D is two-dimensional array (x,y)')


    def rotate(self, angle, degrees = False):
        if degrees:
            angle = math.radians(angle)
            
        return Vector2D(self.length, self.angle + angle, polar = True)

    def normalize(self):
        """Normalized vector"""
        if self.x == 0 and self.y == 0:
            return self
        else:
            return Vector2D(self.x/abs(self), self.y/abs(self))

    def distance_to(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)

    def to_polar(self):
        """Return the vector's components in polar coordinates."""
        return self.length, self.angle
