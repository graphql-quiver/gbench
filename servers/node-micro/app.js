

const cluster = require('cluster');

if(cluster.isMaster) {
    const numWorkers = require('os').cpus().length / 2;

    console.log('Master cluster setting up ' + numWorkers + ' workers...');

    for(let i = 0; i < numWorkers; i++) {
        cluster.fork();
    }

    cluster.on('online', function(worker) {
        console.log('Worker ' + worker.process.pid + ' is online');
    });

    cluster.on('exit', function(worker, code, signal) {
        console.log('Worker ' + worker.process.pid + ' died with code: ' + code + ', and signal: ' + signal);
        console.log('Starting a new worker');
        cluster.fork();
    });
} else {
    const micro = require('micro');
    const graphqlHandler = require('./graphql-handler');
    // The root provides a resolver function for each API endpoint
    const server = micro(graphqlHandler(require("./schema")));

    server.listen(4000);
}

