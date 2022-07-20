============
Introduction
============

This guide describes an architecture to receive and store DICOM images in AWS.  It runs the `Orthanc <https://www.orthanc-server.com>`_ free and open-source, lightweight DICOM server to provide an encrypted DICOMWeb transport for medical images over the internet. The image files are stored as objects in an Amazon S3 bucket, available for further processing. Metadata of each DICOM image is stored in a NoSQL database for fast querying of any attribute of the images.

This architecture comprises the following:

* Orthanc runs as a resilient, scalable containerized service on `Amazon Elastic Container Service <https://aws.amazon.com/ecs/>`_.
* The `Orthanc Docker image <https://book.orthanc-server.com/users/docker-osimis.html>`_ provided by `Osimis <https://www.osimis.io>`_, is used to provide an up to date Orthanc release with all plugins configurable through environment variables.  No state is stored in the containerized application, so the tasks making up the Orthanc service may be started and terminated without any configuration.
* All Orthanc configuration options and secrets are securely stored in `AWS Systems Manager Parameter Store <https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html>`_.
* An AWS `Application Load Balancer <https://aws.amazon.com/elasticloadbalancing/application-load-balancer/>`_ provides an HTTPS front-end for the Orthanc service.
* `AWS Certificate Manager <https://aws.amazon.com/certificate-manager/>`_ provides SSL/TLS certificates for the HTTPS transport.
* `Amazon RDS <https://aws.amazon.com/rds/>`_ is used to store the index of the DICOM images received and stored by the Orthanc application in a PostgreSQL database. 
* An `Amazon S3 <https://aws.amazon.com/s3/>`_ bucket stores the received DICOM images.  S3 buckets are highly durable and have no effective size limit, so a single bucket is sufficient to store any quantity of images.  The DICOM image objects are guaranteed to have unique names, so no storage hierarchy is required within the bucket.
* Each DICOM image object that arrives in the S3 bucket triggers a notification event which is sent to an `Amazon Simple Queue Service <https://aws.amazon.com/sqs/>`_ (SQS) queue. 
* An `AWS Lambda <https://aws.amazon.com/lambda/>`_ Python function consumes the messages from the SQS queue. The function reads the header of the DICOM image S3 object corresponding to each message, and parses this header into a JSON document using the `PyDicom <https://pydicom.github.io/>`_ library.
* The DICOM header metadata is written to a `DynamoDB <https://aws.amazon.com/dynamodb/>`_ table, using the object's S3 key as a key value. From DynamoDB the data may be analyzed using a number of AWS analytics services.
* Encryption is employed in transit during internet transport, and in communication between the Orthanc application and the PostgreSQL database and S3 bucket.  
* Encryption of data is employed at rest in the S3 bucket, and the RDS and DynamoDB databases.
* All the services used are `HIPAA eligible <https://aws.amazon.com/compliance/hipaa-eligible-services-reference/>`_.  With additional configuration, it may be possible for this solution to be used as part of a HIPAA compliant workflow.