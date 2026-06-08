Moving a portion of a diagram has a simple UI: select the portion, then drag and drop it in its new position. But what if the mobile portion has connections to the immobile portion?

Consistent with EDA tools like KiCAD, we are going to implement rubber banding: dynamic updates to connection paths between mobile and immobile portions so that connectivity is preserved as far as possible. Note that the user may deliberately place the mobile portion so that its connections touch down on other connections, causing a connectivity (netlist) change.

This standalone document will evolve from a loose, incomplete and disordered set of statements about and examples of the problem towards a clear set of plain language rules that can drive the implementation of this feature.

Notes:
1. ConnectEd's UI already makes a distinction between movement with rubber banding (slide) vs unconditional movement (move).
2. Non-ortho segments should not normally exist. If they do, they are excluded from rubber banding.

===

Rubber banding is implemented by dynamic connection paths (DCPs) during the slide interaction - these preview the othogonal segments that will be created if the user drops the mobile portion.

The problem arises in 2 scenarios:
  1. segment with 1 mobile and 1 immobile endpoint: segment becomes DCP
  2. selected segment with 2 immobile endpoints: segment mobile, DCPs between mobile endpoints (free nodes) and original/immobile endpoints

Note that The conversion of a DCP to segments cleans up orphan segments. These may arise when a DCP starts on an degree-1 free node.

Implementation detail: the interaction uses an internal QUndoStack to record the transition into and out of the preview state.

Problem: DCPs should cooperate to avoid shorts/overlaps where jogs are added. Suggestion: consider bounding rects of DCPs and assemble sets of those that overlap, enforcing cooperation.

===

DCPs

1. Respect escape direction at both ends.
2. Alternate axis: escape - !escape - escape

===

The big challenge: adding jogs to straight segments.

When a straight segment connects a mobile fixed node to an immobile fixed node, then a jog must be added if the mobile node moves laterally w.r.t the segment. Where the jogs of adjacent segments can interfere, there is extra difficulty.

proposal:

jog_targets = { Axis.H : [], Axis.V : [] }
jog_sets    = { Axis.H : [], Axis.V : [] }
for axis in Axis:
  jog_targets = []
  for seg in affected_segments:
    if seg.isOrthogonal() and seg.axis == ~axis:
      jog_targets.append(seg)
  for segment in jog_targets.copy():  # list will be modified in loop
    for other_set in jog_sets[axis]:
      for other_seg in other_set:
        if seg.brect touches other_seg.brect:
          other_set.add(seg)
    else:
      jog_sets[axis].append(set(seg)) # set of 1



get after bounding rect for all s



===


Scenarios

seg - nothing

seg - corner - seg - nothing

seg - junction

seg - pin/port

seg - corner - seg - pin/port
