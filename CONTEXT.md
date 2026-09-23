# Wanxiang domain glossary

This glossary names the domain concepts used by the workbench and authoring guides. It intentionally excludes file paths, build commands, and implementation decisions.

## Asset

An **asset** is a catalogue entry that can be selected, inspected, composed, or exported. Styles, palettes, dimensions, and internal helpers are properties or implementation aids; they are not separate public assets.

## Part

A **part** is a reusable semantic shape with parameters, materials, an author coordinate frame, and optional connection or consumer metadata. A part can be used by another part or by an assembly.

## Assembly

An **assembly** is a named arrangement of parts and child assemblies with transforms, parameters, and connection intent. It describes how parts are composed; it does not by itself provide game behavior or a physics world.

## Scene

A **scene** is a complete consumer-facing arrangement of assets, including the placement and state of its assemblies. A scene can be exported as a GLB while remaining editable through its source description.

## Author source

**Author source** is the editable definition from which catalogue assets are generated. Generated catalogue records and previews are outputs of author source, not alternate sources of truth.

## Author datum

An **author datum** is a named position, direction, or frame chosen to align related geometry. It is an alignment reference; it does not promise a CAD snap joint or a physical constraint.

## Interface

An **interface** is a versioned connection contract describing compatible geometry, orientation, dimensions, and tolerances. A matching label alone is insufficient to establish a valid connection.

## State control

A **state control** is a declared bounded change to an assembly or part, such as a rotation or translation. It expresses an editable state; it is not a general animation controller, inverse-kinematics solver, or gameplay system.

## Collision intent

**Collision intent** is metadata describing the shape and ownership a consuming engine may use for collision or interaction. It is not a delivered physics implementation, character controller, trigger runtime, or navigation system.

## LOD

**LOD** means a geometry detail level authored for the same asset identity and semantic frame. It is a representation choice, not a new asset family and not an automatic distance-switching system.

## Runtime recipe

A **runtime recipe** is consumer input describing collision, interaction, effects, or static export choices for an asset or assembly. A recipe records intent and source relationships; the consuming game or engine provides execution.

## Evidence

**Evidence** is a record tied to a specific run, environment, and scope. Static checks, CPU rendering, browser checks, device checks, and target-engine checks are distinct kinds of evidence and cannot be substituted for one another.
