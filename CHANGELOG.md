## [1.2] - 2025-11-07

### Changed

- Updated structure within add-in for .jsl code to be seperate files, as opposed ot running in the "Run this JSL" box. No code or feature changes.
  - Allows for quicker and more transparent updates in the future. 

## [1.1] - 2025-11-06

### Added

- Support for Lot level formulation info via new import types:
- Products, Avg Results, Parameter BY LOT - Very similar to Products, Avg Results, and Parameters and holds the same column structure, with the addition of Product / Formula Lot #, providing an extra layer of data.
  - Both Vertical & Horizontal views will copy values for Ingredients & Process Design values to Formula lots, and then hide the "blank" parent that does not have an assigned lot number. 
- Combined Lot Level Avg & Raw Values - Combines the above table with the All Raw Result Data, giving both raw and average result values for lots. Like the Create Both (Combined) table, these two tables will be auto-joined in a standard. optimal format.
  - Both Vertical & Horizontal views will copy values for Ingredients & Process Design values to Formula lots, and then hide the "blank" parent that does not have an assigned lot number.
  - String -> Numeric will auto trigger in horizontal views. 

### Fixed

- Corrected Issue with Lot & Manufacturer lot numbers not always importing. This was due to them sometimes being treated as numbers leading to subtraction calculations on the - seperator.
- Corrected problem in _Create Both (Combined)_ where average value & raw value columns were not receiving column name updates correctly. 

### Changed

- All initial imports will always be strings (JMP type = Character). String -> Numeric JMP script updated and added to all transformation layers. 


