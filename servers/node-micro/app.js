const cluster = require('cluster');

if(cluster.isMaster) {
    const numWorkers = require('os').cpus().length;

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
    const micro = require('micro')
    const graphqlHTTP = require("express-graphql");
    const schema = require("./schema");
    // The root provides a resolver function for each API endpoint
    const server = micro(
        graphqlHTTP({
            schema: schema,
            graphiql: false
        }))

    server.listen(4000);
}
