# Description of the hierarchy model

## GeometrySprite
A basic class that defines the entire workflow for geometric shapes.

Geometric shapes are defined by a structured series of points. They store their
points in a pygame-friendly format for consumption by pygame.draw.xxx

1. compute the shape points position and set them in a proper structure
    that is: number of lines, of triangles...;base size before zooming
    and deformation

   set this in self.points

2. call the set geometric transformers
     zoom; scroll; rotate; 3D projection; projection on a plane
     These transformations operate on points and need a center.

3. compute surface size, draw it
    normally pygame will take care of not rendering whatever is off-screen.


## PolygonSprite

A subclass of GeometrySprite that helps with all pygame.draw.polygon figures.
Subclass this for polygonal geometry.

## LineSprite

A subclass of GeometrySprite that helps with all pygame.draw.line figures.
Subclass this for line drawing and so on.


