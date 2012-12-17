import vtk
import sys

def main(vector_file, magnitude_file):


        num_critical_points = 4
	CriticalPoints = vtk.vtkPoints()
	CriticalPoints.InsertNextPoint(38.6, 26, 32)
	CriticalPoints.InsertNextPoint(16.5, 24.7, 13.5)
	CriticalPoints.InsertNextPoint(24.7, 15, 19)
	CriticalPoints.InsertNextPoint(15.7, 17, 25)

        ColorRange = vtk.vtkLookupTable()
        ColorRange.SetTableRange(0, 1)
        ColorRange.SetHueRange(0, 1)
        ColorRange.SetSaturationRange(1, 1)
        ColorRange.SetAlphaRange(0.3, 0.5)
        ColorRange.Build()

	reader = vtk.vtkStructuredPointsReader()
	reader.SetFileName(vector_file)
	reader.Update()

	mags = reader.GetOutput()
	
        range1 = mags.GetScalarRange()
	v0 = range1[0]
	v1 = range1[1]


	reader_magnitude = vtk.vtkStructuredPointsReader()
	reader_magnitude.SetFileName(magnitude_file)
	reader_magnitude.Update()

        
        #All entities initialized equal to number of critical points
        sphere1, stream1, scalarSurface1, tube1, dataMapper1, dataActor1, criticalMarker1, criticalMapper1, criticalActor1, probe1, mask1, glyph1, glyphMapper1, glyphActor1, plane1 = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
	for i in range(0, num_critical_points):
	    sphere1.append(vtk.vtkSphereSource())
	    stream1.append(vtk.vtkStreamLine())
	    scalarSurface1.append(vtk.vtkRuledSurfaceFilter())
	    tube1.append(vtk.vtkTubeFilter())
	    dataMapper1.append(vtk.vtkPolyDataMapper())
	    dataActor1.append(vtk.vtkActor())

	    criticalMarker1.append(vtk.vtkSphereSource())
	    criticalMapper1.append(vtk.vtkPolyDataMapper())
	    criticalActor1.append(vtk.vtkActor())

	    probe1.append(vtk.vtkProbeFilter())
	    mask1.append(vtk.vtkMaskPoints())
	    glyph1.append(vtk.vtkGlyph3D())
	    glyphMapper1.append(vtk.vtkPolyDataMapper())
	    glyphActor1.append(vtk.vtkActor())

	    plane1.append(vtk.vtkPlaneSource())
      
	integ = vtk.vtkRungeKutta4()
	
        cone = vtk.vtkConeSource()
	cone.SetResolution(8)
	cone.SetHeight(1.0)
	cone.SetRadius(0.2)

	transform = vtk.vtkTransform()
	transform.Translate(0, 0, 0)

	transformFilter = vtk.vtkTransformPolyDataFilter()
	transformFilter.SetInput(cone.GetOutput())
	transformFilter.SetTransform(transform)

	outline = vtk.vtkOutlineFilter()
	outline.SetInput(reader.GetOutput())

	outlineMapper = vtk.vtkPolyDataMapper()
	outlineMapper.SetInput(outline.GetOutput())

	outlineActor = vtk.vtkActor()
	outlineActor.SetMapper(outlineMapper)
	outlineActor.GetProperty().SetColor(1, 1, 1)

	bar = vtk.vtkScalarBarActor()
	bar.SetLookupTable(ColorRange)

        renderer = vtk.vtkRenderer()
      
        for i in range(0, num_critical_points):
                        sphere1[i].SetRadius(2)
                        sphere1[i].SetCenter(CriticalPoints.GetPoint(i)[0], CriticalPoints.GetPoint(i)[1], CriticalPoints.GetPoint(i)[2])
                        sphere1[i].SetThetaResolution(1)
                        stream1[i].SetInput(reader.GetOutput())
                        stream1[i].SetSource(sphere1[i].GetOutput())
                        stream1[i].SetIntegrator(integ)
                        stream1[i].SetMaximumPropagationTime(500)
                        stream1[i].SetIntegrationStepLength(0.1)
                        stream1[i].SetIntegrationDirectionToIntegrateBothDirections()
                        stream1[i].SetStepLength(0.1)

                        scalarSurface1[i].SetInput(stream1[i].GetOutput())
                        scalarSurface1[i].SetOffset(0)
                        scalarSurface1[i].SetOnRatio(2)
                        scalarSurface1[i].PassLinesOn()
                        scalarSurface1[i].SetRuledModeToPointWalk()
                        scalarSurface1[i].SetDistanceFactor(50)

                        tube1[i].SetInput(scalarSurface1[i].GetOutput())
                        tube1[i].SetRadius(0.1)
                        tube1[i].SetNumberOfSides(6)

                        dataMapper1[i].SetInput(tube1[i].GetOutput())
                        dataMapper1[i].SetScalarRange(v0, v1)
                        dataMapper1[i].SetLookupTable(ColorRange)

                        dataActor1[i].SetMapper(dataMapper1[i])
                        renderer.AddActor(dataActor1[i])

                        criticalMarker1[i].SetRadius(1.0)
                        criticalMarker1[i].SetCenter(CriticalPoints.GetPoint(i)[0], CriticalPoints.GetPoint(i)[1], CriticalPoints.GetPoint(i)[2])
                        criticalMarker1[i].SetThetaResolution(10)
                        criticalMapper1[i].SetInput(criticalMarker1[i].GetOutput())

                        criticalActor1[i].SetMapper(criticalMapper1[i])
                        criticalActor1[i].GetProperty().SetColor(1, 1, 0)
                        criticalActor1[i].GetProperty().SetOpacity(0.5)
                        renderer.AddActor(criticalActor1[i])

                        probe1[i].SetInput(stream1[i].GetOutput())
                        probe1[i].SetSource(reader.GetOutput())

                        mask1[i].SetInput(probe1[i].GetOutput())
                        mask1[i].SetOnRatio(60)
                        mask1[i].RandomModeOn()

                        glyph1[i].SetInput(mask1[i].GetOutput())
                        glyph1[i].SetSource(transformFilter.GetOutput())
                        glyph1[i].SetScaleModeToScaleByVector()
                        glyph1[i].SetScaleFactor(2)
                        glyph1[i].SetVectorModeToUseVector()
                        glyph1[i].SetColorModeToColorByVector()

                        glyphMapper1[i].SetInput(glyph1[i].GetOutput())
                        glyphMapper1[i].SetLookupTable(ColorRange)

                        glyphActor1[i].SetMapper(glyphMapper1[i])
                        renderer.AddActor(glyphActor1[i])

        renderer_window = vtk.vtkRenderWindow()
        renderer_window.AddRenderer(renderer)
        renderer_window.SetSize(512,512)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(renderer_window)

        style = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)

        renderer.AddActor(bar)

        renderer.AddActor(outlineActor)

        renderer_window.Render()
        interactor.Start()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "The command line format is 'python %s <vector_file> <magnitude_file>'"
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
