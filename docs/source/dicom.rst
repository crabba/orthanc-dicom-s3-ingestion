=====
DICOM
=====

This solution is designed to receive DICOM images transported across the internet, store the images, and make them available for processing using analytic, machine learning, or general purpose services in AWS. 

The DICOM transport is provided by a `DICOMWeb <https://www.dicomstandard.org/using/dicomweb>`_ endpoint to the internet.  DICOMWeb comprises a family of REST services for the storage (the `STOW-RS <https://www.dicomstandard.org/using/dicomweb/store-stow-rs>`_ service), retrieval (`WADO-RS <https://www.dicomstandard.org/using/dicomweb/retrieve-wado-rs-and-wado-uri>`_, and querying (`QIDO-RS <https://www.dicomstandard.org/using/dicomweb/query-qido-rs>`_) of structured collections of medical images.  This documentation refers only to the STOW-RS service, but the query and retrieval services are also available through the same endpoint.

The storage, retrieval and querying processes may be performed at the level of individual images (instances), or collections of images at the series or study level.  For a more detailed explanation of the DICOM data model, refer to:

* `DCM4CHE: A Very Basic DICOM Introduction <https://dcm4che.atlassian.net/wiki/spaces/d2/pages/1835038/A+Very+Basic+DICOM+Introduction>`_
* `Towards Data Science: Understanding DICOM <https://towardsdatascience.com/understanding-dicom-bce665e62b72>`_
* `DICOM is Easy: Introduction to DICOM - Chapter 4 - DICOM Objects <http://dicomiseasy.blogspot.com/2011/12/chapter-4-dicom-objects-in-chapter-3.html>`_

