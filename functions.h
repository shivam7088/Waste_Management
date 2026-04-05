#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_HEAP 100

typedef struct {
    int id;
    char area[30];
    int fill;       //! 0-100
    int priority;   //! smaller value => more urgent
} Request;

// Queue
typedef struct Node {
    Request data;
    struct Node *next;
} Node;

typedef struct {
    Node *front, *rear;
} Queue;

void initQueue(Queue *q);
int isQueueEmpty(Queue *q);
void enqueue(Queue *q, Request r);
int dequeue(Queue *q, Request *r);
void displayQueue(Queue *q);
void displayQueueByArea(Queue *q, const char *area);

// Min Heap
typedef struct {
    Request *arr;
    int size;
    int capacity;
} MinHeap;

void initHeap(MinHeap *h, int capacity);
void heapifyUp(MinHeap *h, int i);
void heapifyDown(MinHeap *h, int i);
void insertHeap(MinHeap *h, Request r);
int extractMin(MinHeap *h, Request *out);
void displayHeap(MinHeap *h);

int idExists(Queue *q, MinHeap *h, int id);
void adminChooseBin(MinHeap *h);

#endif
