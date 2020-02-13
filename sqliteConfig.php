<?php

class myDB extends SQLite3
{
	function __construct()
	{
		$this->open('C:\\xampp\\htdocs\\ChatBot_v4\\chat_system.db');
	}
}

$SQLitedb = new myDB();
?>