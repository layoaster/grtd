// Mongo Shell script to add and index (ldap) on the agentStatus collections
// 
// Usage: 'mongo index_agent.js'

// Connecting to a mongo instance
cnx = new Mongo("localhost")
db = cnx.getDB("test");

// Adding the ldap index
db.agentStatus.ensureIndex{'ldap':1})
