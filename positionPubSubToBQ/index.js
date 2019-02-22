/**
 * Triggered from a message on a Cloud Pub/Sub topic.
 *
 * @param {!Object} event Event payload and metadata.
 * @param {!Function} callback Callback function to signal completion.
 */
var BigQuery = require('@google-cloud/bigquery');
var projectId = 'YOUR-PROJECT-ID-HERE'; // IMPORTANT!! Enter your project ID here
var datasetName = 'iotData';
var tableName = 'position_data';

var bigquery = new BigQuery({
    projectId: projectId,
});

exports.subscribe = function (event, callback) {
    var msg = event.data;
    var incomingData = msg.data
        ? Buffer.from(msg.data, 'base64').toString()
        : "{'timestamp':'1/1/1970 00:00:00','device_id':'', 'accel_x':'0', 'accel_y':'0', 'accel_z':'0', 'direction': '0'}";
    var data = JSON.parse(incomingData);


    // console.log(data); 
    bigquery
        .dataset(datasetName)
        .table(tableName)
        .insert(data)
        .then(function () {
            console.log('Inserted rows');
            callback(); // task done 
        })
        .catch(function (err) {
            if (err && err.name === 'PartialFailureError') {
                if (err.errors && err.errors.length > 0) {
                    console.log('Insert errors:');
                    err.errors.forEach(function (err) {
                        console.error(err);
                    });
                }
            } else {
                console.error('ERROR:', err);
            }

            callback(); // task done 
        });
};
