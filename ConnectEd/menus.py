menus = [
    [ "File", [
        [ "New"              , "fileNew"            ],
        [ "Open"             , "fileOpen"           ],
        [ "Save"             , "fileSave"           ],
        [ "Save As..."       , "fileSaveAs"         ],
        [ "Close"            , "fileClose"          ],
        [ ""                 , None                 ],
        [ "Export"           , "fileExport"         ],
        [ "Import"           , "fileImport"         ],
        [ ""                 , None                 ],
        [ "Print"            , "filePrint"          ],
        [ "Print Preview"    , "filePrintPreview"   ],
        [ "Page Setup"       , "filePageSetup"      ]
    ]],
    [ "Edit", [
        [ "Cancel"           , "editCancel"         ],
        [ "Undo"             , "editUndo"           ],
        [ "Redo"             , "editRedo"           ],
        [ ""                 , None                 ],
        [ "Cut"              , "editCut"            ],
        [ "Copy"             , "editCopy"           ],
        [ "Paste"            , "editPaste"          ],
        [ "Delete"           , "editDelete"         ],
        [ "Select All"       , "editSelectAll"      ],
        [ ""                 , None                 ],
        [ "Find"             , "editFind"           ],
        [ "Replace"          , "editReplace"        ],
        [ "Select All"       , "editSelectAll"      ],
        [ "Select Filter..." , "editSelectFilter"   ]
    ]],
    [ "Element", [
        [ "Block"            , "elementBlock"       ], # component or entity instance; process; function
        [ "Pin"              , "elementPin"         ],
        [ "Wire"             , "elementWire"        ],
        [ "Tap"              , "elementTap"         ], # bus tap
        [ "Junction"         , "elementJunction"    ],
        [ "Port"             , "elementPort"        ],
        [ "Connection"       , "elementConnection"  ], # describes connections e.g. reset port -> all blocks
        [ "Property"         , "elementProperty"    ],
        [ "Code"             , "elementCode"        ]
    ]],
    [ "Graphic", [
        [ "Line"             , "graphicLine"        ],
        [ "Rectangle"        , "graphicRectangle"   ],
        [ "Polygon"          , "graphicPolygon"     ],
        [ "Arc"              , "graphicArc"         ],
        [ "Ellipse"          , "graphicEllipse"     ],
        [ "Image..."         , "graphicImage"       ],
        [ ""                 , None                 ],
        [ "Text Line"        , "graphicTextLine"    ],
        [ "Text Box"         , "graphicTextBox"     ]
    ]],
    [ "View", [
        [ "Zoom In"          , "viewZoomIn"         ],
        [ "Zoom Out"         , "viewZoomOut"        ],
        [ "Zoom Window"      , "viewZoomWindow"     ],
        [ "Zoom Full"        , "viewZoomFull"       ],
        [ ""                 , None                 ],
        [ "Pan Left"         , "viewPanLeft"        ],
        [ "Pan Right"        , "viewPanRight"       ],
        [ "Pan Up"           , "viewPanUp"          ],
        [ "Pan Down"         , "viewPanDown"        ]
    ]],
    [ "Options" , [
        [ "Preferences"      , "optionsPreferences" ]
    ]],
    [ "Help", [
        [ "About"            , "helpAbout"          ]
    ]]
]
