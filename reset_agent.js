// Mongo Shell script to perform a data reset on the agentStatus collection
// 
// Usage: 'mongo agent_reset.js'

// Connecting to a mongo instance
cnx = new Mongo("localhost")
db = cnx.getDB("test");

// Dropping the agentStatus collection
db.agentStatus.remove({})
