#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include "functions.h"
//?Queue 
void initQueue(Queue *q) { q->front = q->rear = NULL; }
int isQueueEmpty(Queue *q) { return q->front == NULL; }

void enqueue(Queue *q, Request r) {
    Node *newNode = (Node*)malloc(sizeof(Node));
    newNode->data = r;
    newNode->next = NULL;
    if (q->rear == NULL) q->front = q->rear = newNode;
    else { q->rear->next = newNode; q->rear = newNode; }
    printf("Added request ID %d to queue.\n", r.id);
} 

// ?Removes the earliest request from the queue and returns it.
int dequeue(Queue *q, Request *r) {
    if (isQueueEmpty(q)) return 0;
    Node *temp = q->front;
    *r = temp->data;
    q->front = q->front->next;
    if (q->front == NULL) q->rear = NULL;
    free(temp);
    return 1;
}

void displayQueue(Queue *q) {
    if (isQueueEmpty(q)) {
        printf("Queue is empty.\n");
        return;
    }
    Node *cur = q->front;
    printf("\n-- Queue Contents --\n");
    while (cur) {
        printf("ID:%d  Area:%s  Fill:%d%%  Priority:%d\n",
               cur->data.id, cur->data.area, cur->data.fill, cur->data.priority);
        cur = cur->next;
    }
    printf("--------------------\n");
}

static int equalsIgnoreCase(const char *a, const char *b) {
    while (*a && *b) {
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b)) return 0;
        a++;
        b++;
    }
    return *a == '\0' && *b == '\0';
}

void displayQueueByArea(Queue *q, const char *area) {
    if (isQueueEmpty(q)) {
        printf("Queue is empty.\n");
        return;
    }

    Node *cur = q->front;
    int found = 0;
    while (cur) {
        if (equalsIgnoreCase(cur->data.area, area)) {
            if (!found) printf("\n-- Queue Contents for %s --\n", area);
            printf("ID:%d  Area:%s  Fill:%d%%  Priority:%d\n",
                   cur->data.id, cur->data.area, cur->data.fill, cur->data.priority);
            found = 1;
        }
        cur = cur->next;
    }

    if (!found) printf("No bins found for area %s.\n", area);
    else printf("-------------------------------\n");
}

/* ------------------ Min Heap ------------------ */
//? Min Heap keeps smallest priority (most urgent) at index 0.

void initHeap(MinHeap *h, int capacity) {
    h->arr = (Request*)malloc(capacity * sizeof(Request));
    h->size = 0;
    h->capacity = capacity;
}

void swap(Request *a, Request *b) { Request t = *a; *a = *b; *b = t; }

//!heapifyUp is used when adding a new request.
void heapifyUp(MinHeap *h, int i) {
    while (i > 0) {
        int p = (i - 1) / 2;
        if (h->arr[p].priority <= h->arr[i].priority) break;
        swap(&h->arr[p], &h->arr[i]);
        i = p;
    }
}

//!heapifyDown is used when removing the root.
void heapifyDown(MinHeap *h, int i) {
    while (1) { 
        int l = 2 * i + 1, r = 2 * i + 2, s = i;
        if (l < h->size && h->arr[l].priority < h->arr[s].priority) s = l;
        if (r < h->size && h->arr[r].priority < h->arr[s].priority) s = r;
        if (s == i) break;
        swap(&h->arr[i], &h->arr[s]);
        i = s;
    }
}
//!insert heap
void insertHeap(MinHeap *h, Request r) {
    if (h->size == h->capacity) {
    int new_cap = h->capacity * 2;
    Request* temp = (Request*)realloc(h->arr, new_cap * sizeof(Request));
    if (temp == NULL) {
        printf("Memory allocation failed!\n");
        return; // Safety exit
    }
    h->arr = temp;
    h->capacity = new_cap;
}
    h->arr[h->size] = r;
    heapifyUp(h, h->size);
    h->size++;
}

int extractMin(MinHeap *h, Request *out) {
    if (h->size == 0) return 0;
    *out = h->arr[0];
    h->arr[0] = h->arr[h->size - 1];
    h->size--;
    heapifyDown(h, 0);
    return 1;
}

void displayHeap(MinHeap *h) {
    if (h->size == 0) { printf("Heap is empty.\n"); return; }
    printf("\n-- Heap (by priority) --\n");
    for (int i = 0; i < h->size; i++) {
        Request r = h->arr[i];
        printf("[%d] ID:%d  Area:%s  Fill:%d%%  Priority:%d\n",
               i, r.id, r.area, r.fill, r.priority);
    }
    printf("------------------------\n");
}


int idExists(Queue *q, MinHeap *h, int id) {
    Node *cur = q->front;
    while (cur) {
        if (cur->data.id == id) return 1;
        cur = cur->next;
    }
    for (int i = 0; i < h->size; i++) {
        if (h->arr[i].id == id) return 1;
    }
    return 0;
}


void adminChooseBin(MinHeap *h) {
    if (h->size == 0) {
        printf("No bins in heap.\n");
        return;
    }
    displayHeap(h);
    int id;
    printf("Enter ID of bin to clean: ");
    scanf("%d", &id);

    int found = -1;
    for (int i = 0; i < h->size; i++) {
        if (h->arr[i].id == id) { found = i; break; }
    }
    if (found == -1) {
        printf("Bin ID not found.\n");
        return;
    }

    printf("Cleaning bin ID:%d (%s)... Done.\n", h->arr[found].id, h->arr[found].area);
    h->arr[found] = h->arr[h->size - 1];
    h->size--;
    
    if (found > 0 && h->arr[found].priority < h->arr[(found - 1) / 2].priority) {
        heapifyUp(h, found);
    } else {
        heapifyDown(h, found);
    }
}
