Vagrant.configure("2") do |config|
	M1_IP = "52.16.139.42"
	M2_IP = "34.247.193.119"

	config.vm.define "m1" do |m1|
		m1.vm.box = "dummy"

		m1.vm.provider :aws do |aws, override|
			aws.ami = "ami-0c21ae4a3bd190229"
	    aws.region="eu-west-1"
			aws.instance_type="t2.micro"
			aws.keypair_name="cloudcomputing"
			aws.elastic_ip=M1_IP

			override.ssh.username="ec2-user"
			override.ssh.private_key_path =
				"/home/jacoboqc/Documentos/Máster/Materias/2º curso/Cloud Computing/Project/cloudcomputing.pem"
	  end

		m1.vm.provision "shell",
			inline: "touch test.txt"
	end

	config.vm.define "m2" do |m2|
		m2.vm.box = "dummy"

		m2.vm.provider :aws do |aws, override|
			aws.ami = "ami-0c21ae4a3bd190229"
	    aws.region="eu-west-1"
			aws.instance_type="t2.micro"
			aws.keypair_name="cloudcomputing"
			aws.elastic_ip=M2_IP

			override.ssh.username="ec2-user"
			override.ssh.private_key_path =
				"/home/jacoboqc/Documentos/Máster/Materias/2º curso/Cloud Computing/Project/cloudcomputing.pem"
	  end

		m2.vm.provision "shell",
			inline: "touch test.txt"
	end
end
