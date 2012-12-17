import vtk
import sys

def main(vector_file, magnitude_file):
    
        ColorRange = vtk.vtkLookupTable()
        ColorRange.SetTableRange(0, 1)
        ColorRange.SetHueRange(0, 1)
        ColorRange.SetSaturationRange(1, 1)
        ColorRange.SetAlphaRange(0.3, 0.5)
        ColorRange.Build()

	reader = vtk.vtkStructuredPointsReader()
	reader.SetFileName(vector_file)
	reader.Update()

	data = reader.GetOutput()

	range1 = data.GetScalarRange()
	v0 = range1[0]
	v1 = range1[1]

	reader_magnitude = vtk.vtkStructuredPointsReader()
	reader_magnitude.SetFileName(magnitude_file)
	reader_magnitude.Update()

	contour = vtk.vtkContourFilter()
	contour.SetInput(reader_magnitude.GetOutput())
	contour.SetValue(0, 1)

	normals = vtk.vtkPolyDataNormals()
	normals.SetInput(contour.GetOutput())
	normals.SetFeatureAngle(60)
	normals.ConsistencyOff()
	normals.SplittingOff()

        mapper_magnitude = vtk.vtkPolyDataMapper()
        mapper_magnitude.SetInput(normals.GetOutput())
        mapper_magnitude.SetLookupTable(ColorRange)
        mapper_magnitude.SetColorModeToMapScalars()
        mapper_magnitude.SetScalarRange(v0, v1)

	actor_magnitude = vtk.vtkActor()
	actor_magnitude.SetMapper(mapper_magnitude)

        sphere = vtk.vtkSphereSource()
	sphere.SetRadius(2)
	sphere.SetCenter(15, 15, 15) # Critical point for all 3 test datasets
	sphere.SetThetaResolution(10)

	integrator = vtk.vtkRungeKutta4()

	stream = vtk.vtkStreamLine()
	stream.SetInput(reader.GetOutput())
	stream.SetSource(sphere.GetOutput())
	stream.SetIntegrator(integrator)
	stream.SetMaximumPropagationTime(500)
	stream.SetIntegrationStepLength(0.1)
	stream.SetIntegrationDirectionToIntegrateBothDirections()
	stream.SetStepLength(0.1)

	scalarSurface = vtk.vtkRuledSurfaceFilter()
	scalarSurface.SetInput(stream.GetOutput())
	scalarSurface.SetOffset(0)
	scalarSurface.SetOnRatio(2)
	scalarSurface.PassLinesOn()
	scalarSurface.SetRuledModeToPointWalk()
	scalarSurface.SetDistanceFactor(50)

	tube = vtk.vtkTubeFilter()
	tube.SetInput(scalarSurface.GetOutput())
	tube.SetRadius(0.1)
	tube.SetNumberOfSides(6)

	dataMapper = vtk.vtkPolyDataMapper()
	dataMapper.SetInput(tube.GetOutput())
	dataMapper.SetScalarRange(v0, v1)
	dataMapper.SetLookupTable(ColorRange)

	dataActor = vtk.vtkActor()
	dataActor.SetMapper(dataMapper)

	probe = vtk.vtkProbeFilter()
	probe.SetInput(stream.GetOutput())
	probe.SetSource(reader.GetOutput())

	mask = vtk.vtkMaskPoints()
	mask.SetInput(probe.GetOutput())
	mask.SetOnRatio(60)
	mask.RandomModeOn()

	cone = vtk.vtkConeSource()
	cone.SetResolution(8)
	cone.SetHeight(1.0)
	cone.SetRadius(0.2)

	transform = vtk.vtkTransform()
	transform.Translate(0, 0, 0)

	transformFilter = vtk.vtkTransformPolyDataFilter()
	transformFilter.SetInput(cone.GetOutput())
	transformFilter.SetTransform(transform)

	glyph = vtk.vtkGlyph3D()
	glyph.SetInput(mask.GetOutput())
	glyph.SetSource(transformFilter.GetOutput())
	glyph.SetScaleModeToScaleByVector()
	glyph.SetScaleFactor(1.5)
	glyph.SetVectorModeToUseVector()
	glyph.SetColorModeToColorByVector()

	glyphMapper = vtk.vtkPolyDataMapper()
	glyphMapper.SetInput(glyph.GetOutput())
	glyphMapper.SetLookupTable(ColorRange)

	glyphActor = vtk.vtkActor()
	glyphActor.SetMapper(glyphMapper)

	outline = vtk.vtkOutlineFilter()
	outline.SetInput(reader.GetOutput())

	outlineMapper = vtk.vtkPolyDataMapper()
	outlineMapper.SetInput(outline.GetOutput())

	outlineActor = vtk.vtkActor()
	outlineActor.SetMapper(outlineMapper)
	outlineActor.GetProperty().SetColor(1, 1, 1)

	criticalMarker = vtk.vtkSphereSource()
	criticalMarker.SetRadius(1.0)
	criticalMarker.SetCenter(15, 15, 15)
	criticalMarker.SetThetaResolution(10)

	criticalMapper = vtk.vtkPolyDataMapper()
	criticalMapper.SetInput(criticalMarker.GetOutput())

	criticalActor = vtk.vtkActor()
	criticalActor.SetMapper(criticalMapper)
	criticalActor.GetProperty().SetColor(1, 1, 0)
	criticalActor.GetProperty().SetOpacity(0.5)

        colorActor = vtk.vtkScalarBarActor()
        colorActor.SetLookupTable(ColorRange)

	renderer = vtk.vtkRenderer()

	renderer_window = vtk.vtkRenderWindow()
	renderer_window.AddRenderer(renderer)
	renderer_window.SetSize(512,512)

	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(renderer_window)
	renderer.AddActor(actor_magnitude)
	renderer.AddActor(outlineActor)
        renderer.AddActor(criticalActor)
        renderer.AddActor(colorActor)
        renderer.AddActor(dataActor)
        renderer.AddActor(glyphActor)

	renderer.ResetCamera()

	style = vtk.vtkInteractorStyleTrackballCamera()
        #style = vtk.vtkInteractorStyleRubberBandZoom()
        #style = vtk.vtkInteractorStyleTerrain()
	interactor.SetInteractorStyle(style)

	renderer_window.Render()
        interactor.Start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "The command line format is 'python %s <vector_file> <magnitude_file>'"
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
