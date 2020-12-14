/* Version : ISO C++11 */
#include<iostream>
#include<string>
#include<conio.h>
#include<thread>
#include<vector>

#define EXIT_KEY 17
#define ENTER_KEY 13
#define BACKSPACE 8
#define BUFFER_SIZE 100

static int i = 0;
char arr[BUFFER_SIZE];
using namespace std;

class Keyboard
{
public:
	int c;
	char ch;
public:
	Keyboard(int c) :c(c), ch(c){}

	virtual void operation() = 0;

	void appendToBuffer(){
		arr[i++] = ch;
	}

	void removeFromBuffer(){
		arr[--i] = ' ';
	}

	void dispaly(){
		cout << arr << endl;
	}

	void clearBuffer(){
		i = 0;
		memset(arr, 0, sizeof arr);
	}
};

class EnterKey :public Keyboard{
public:
	EnterKey(int c) :Keyboard(c){}
	void operation(){
		dispaly();
		clearBuffer();
	}
};

class BackspaceKey :public Keyboard{
public:
	BackspaceKey(int c) :Keyboard(c){}
	void operation(){
		removeFromBuffer();
	}
};

class OtherKeys : public Keyboard{
public:
	OtherKeys(int c) : Keyboard(c){}
	void operation(){
		appendToBuffer();
	}
};

template <class T>
class Smart{
	T* ptr = NULL;

public:
	Smart(T* ptr = NULL) : ptr(ptr)
	{
	}

	T* operator->(){
		return ptr;
	}

	~Smart(){
		if (ptr != NULL){
			delete ptr;
		}
	}
};

auto CheckKey = [](int key){
	if (key == BACKSPACE){
		Smart<BackspaceKey> bck(new BackspaceKey(key));
		bck->operation();
	}
	else if (key == ENTER_KEY){
		Smart<EnterKey> ent(new EnterKey(key));
		ent->operation();
	}
	else{
		Smart<OtherKeys> others(new OtherKeys(key));
		others->operation();
	}
};

int main()
{
	int ch;
	cout << "Starting Virtual Keyboard Session(Press ctrl q to exit session)" << endl;
	cout << "------------------------------------------------------------ \n";
	vector<thread> threads;
	while ((ch = _getch()) != EXIT_KEY){
		threads.push_back(thread(CheckKey, ch));
	}
	for (auto &th : threads){
		th.join();
	}
	cout << "------------------------------------------------------------ \n";
	cout << "Virtual Keyboard Session ended successfully" << endl;
	system("pause");
	return 0;
}