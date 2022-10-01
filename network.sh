
function up(){

    service docker start
    docker stop $(docker ps -a -q)
    docker rm $(docker ps -a -q)
    docker network prune
    docker volume prune
    docker image prune
    docker network create iroha-network
    docker run --name some-postgres \
	    -e POSTGRES_USER=postgres \
	    -e POSTGRES_PASSWORD=mysecretpassword \
	    -p 5432:5432 \
	    --network=iroha-network \
	    -d postgres:9.5 \
	    -c 'max_prepared_transactions=100'
    docker volume create blockstore
    # git clone -b main https://github.com/hyperledger/iroha --depth=1
    docker run --name iroha \
	    -d \
	    -p 50051:50051 \
	    -v $(pwd)/iroha/example:/opt/iroha_data \
	    -v blockstore:/tmp/block_store \
	    --network=iroha-network \
	    -e KEY='node1' \
	    hyperledger/iroha:latest

}


function down(){

    docker-compose -f Network-Files/docker-compose.yaml down --volumes --remove-orphans
}

function restart(){
    down
    up
}

"$@"
