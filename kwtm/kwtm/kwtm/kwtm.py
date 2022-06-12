import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# kwtm - Paulina Klimanek - 09.06.2022
#

class kwtm(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "kwtm" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
It performs a simple thresholding on the input volume and optionally captures a screenshot.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# kwtmWidget
#

class kwtmWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...
    # Parameters Area -
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)


    # input model selector
    self.inputModelSelector = slicer.qMRMLNodeComboBox()
    self.inputModelSelector.nodeTypes = ["vtkMRMLModelNode"]
    self.inputModelSelector.selectNodeUponCreation = True
    self.inputModelSelector.addEnabled = False
    self.inputModelSelector.removeEnabled = False
    self.inputModelSelector.noneEnabled = False
    self.inputModelSelector.showHidden = False
    self.inputModelSelector.showChildNodeTypes = False
    self.inputModelSelector.setMRMLScene(slicer.mrmlScene)
    self.inputModelSelector.setToolTip("Pick the model input to the algorithm.")
    parametersFormLayout.addRow("Input Model: ", self.inputModelSelector)

    # model opacity slider
    self.modelOpacitySliderWidget = ctk.ctkSliderWidget()
    self.modelOpacitySliderWidget.singleStep = 0.1
    self.modelOpacitySliderWidget.minimum = 0.0
    self.modelOpacitySliderWidget.maximum = 100.0
    self.modelOpacitySliderWidget.value = 70.0
    self.modelOpacitySliderWidget.setToolTip("Set opacity value for computing the model.")
    parametersFormLayout.addRow("Model opacity:", self.modelOpacitySliderWidget)

    # apply button - changes model opacity
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Change opacity of a model."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # visibility button - changes model visibility
    self.visibilityOnOffButton = qt.QPushButton("Model visibility On/Off")
    self.visibilityOnOffButton.toolTip = "Change model visibility."
    self.visibilityOnOffButton.enabled = True
    parametersFormLayout.addRow(self.visibilityOnOffButton)

    # connections
    self.inputModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.applyButton.connect('clicked(bool)', self.onOpacityButton)
    self.visibilityOnOffButton.connect('clicked(bool)', self.onVisibilityButton)


    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()


  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputModelSelector.currentNode()

  def onOpacityButton(self):
    logic = kwtmLogic()
    modelOpacityValue = self.modelOpacitySliderWidget.value
    logic.changeOpacity(self.inputModelSelector.currentNode(), modelOpacityValue)

  def onVisibilityButton(self):
    logic = kwtmLogic()
    logic.changeVisibility(self.inputModelSelector.currentNode())

#
# kwtmLogic
#

class kwtmLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self, volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasPolyData failed: no volume node')
      return False
    if volumeNode.GetPolyData() is None:
      logging.debug('hasPolyData failed: no image data in volume node')
      return False
    return True


  def changeOpacity(self, inputModel, modelOpacityValue):
    """
    Change opacity of a selected model based on a value from slider
    """

    logging.info('Processing started')

    model = inputModel.GetDisplayNode()
    model.SetOpacity(modelOpacityValue / 100.0)
    print(modelOpacityValue)

    logging.info('Processing completed - opacity changed')

    return True


  def changeVisibility(self, inputModel):
    """
    Run the actual algorithm
    """

    logging.info('Processing started')

    model = inputModel.GetDisplayNode()
    if model.GetVisibility() == 0:
      model.VisibilityOn()
      logging.info('Model visibility enabled')
    else:
      model.VisibilityOff()
      logging.info('Model visibility disabled')

    logging.info('Processing completed')

    return True


class kwtmTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_kwtm1()

  def test_kwtm1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import SampleData
    SampleData.downloadFromURL(
      nodeNames='FA',
      fileNames='FA.nrrd',
      uris='http://slicer.kitware.com/midas3/download?items=5767',
      checksums='SHA256:12d17fba4f2e1f1a843f0757366f28c3f3e1a8bb38836f0de2a32bb1cd476560')
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = kwtmLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
