create table dir_statistic (
	pc varchar2(40),
	description varchar2(200),
	batch_no varchar2(40),
	dir_name varchar2(100),
	dir_path varchar2(500),
	parent_path varchar2(500),
	root_path varchar2(500),
	dir_level number(8),
	child_file_num number(18),
	child_file_num_all number(18),
	child_dir_num number(18),
	child_dir_num_all number(18),
	child_file_size number(18,2),
	child_file_size_all number(18,2),
	child_zero_num number(18),
	child_zero_num_all number(18),
	statistic_time date	
);