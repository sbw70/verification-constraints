# MP004 Notes

This directory preserves limited implementation and publication notes that affect interpretation or reproduction of MP004.

It is not a scored-evidence directory.

## Contents

### `MP004_INSTALL_CORRECTION.txt`

Records a pre-run path correction.

An initial installation command referenced the source from the wrong working directory and failed before any verifier run or evidence directory was created.

The corrected command used the intended source path.

No scored evidence, verifier logic, fixture bytes, or source material changed as a result.

### `PUBLICATION_NOTES.md`

Records publication-specific facts relevant to interpreting the published MP004 package.

The note identifies:

- the selected MP003 source set used by MP004;
- preservation of the scored verifier and original test suite;
- the publication-portable test adaptation;
- successful preflight, scored execution, staging replay, and publication audit;
- the fixed role of the N03 and N04 descriptor files;
- verifier scope and limitations;
- the relationship between the copied `source/MP003/` subset and the complete MP003 module;
- the role of the publication-wide integrity inventory.

## Evidence meaning

The files in this directory document corrections or publication details that could otherwise create ambiguity when reproducing or inspecting MP004.

They do not add scored cases or change the result of the original scored campaign.

## Limits

These notes are explanatory records.

They are not substitutes for:

- the locked test definition under `../configs/`;
- the preserved source under `../source/`;
- the verifier under `../verifier/`;
- the scored evidence under `../evidence/scored/`.

Where a note and a scored artifact describe the same test property, the locked configuration and scored evidence control interpretation.
