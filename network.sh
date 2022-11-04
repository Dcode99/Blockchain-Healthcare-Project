
function up(){

    service docker start
    docker run --name some-postgres \
	    -e POSTGRES_USER=postgres \
	    -e POSTGRES_PASSWORD=mysecretpassword \
	    --net host \
	    -d postgres:9.5 \
	    -c 'max_prepared_transactions=100'
    docker volume create blockstore
    sleep 10s
    docker run --name iroha \
	    -d \
	    --net host \
	    -v $(pwd)/Network-Files/node1:/opt/iroha_data \
	    -v blockstore:/tmp/block_store \
	    -e KEY='node1' \
	    hyperledger/iroha:latest

}


function down(){

    docker stop $(docker ps -a -q)
    docker rm $(docker ps -a -q)
    docker network prune
    docker volume prune
    docker image prune
}

function restart(){
    down
    up
}

"$@"
