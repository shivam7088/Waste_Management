#include <stdio.h>
#include <stdlib.h>
#include "functions.h"

int main() {
    Queue q; 
    MinHeap h;
    initQueue(&q);
    initHeap(&h, 10);

    int role, choice;

    while (1) {
        printf("\n=== Main Menu ===\n");
        printf("1. Login as Admin\n");
        printf("2. Login as User\n");
        printf("3. Exit Program\n");
        printf("Enter choice: ");
        scanf("%d", &role);

        if (role == 1) {
            while (1) {
                printf("\n===== Admin Menu =====\n");
                printf("1. Display Queue\n");
                printf("2. Display Queue by Area\n");
                printf("3. Move Queue -> Heap\n");
                printf("4. Display Heap\n");
                printf("5. Auto clean next (Extract-Min)\n");
                printf("6. Choose bin to clean (by ID)\n");
                printf("7. Logout to Main Menu\n");
                printf("Enter choice: ");
                scanf("%d", &choice);

                if (choice == 1) displayQueue(&q);
                else if (choice == 2) {
                    char area[30];
                    printf("Enter area to filter: ");
                    scanf("%29s", area);
                    displayQueueByArea(&q, area);
                }
                else if (choice == 3) {
                    Request t;
                    while (dequeue(&q, &t)) insertHeap(&h, t); //! Move all requests to heap
                    printf("Moved all requests to heap.\n");
                }
                else if (choice == 4) displayHeap(&h);
                else if (choice == 5) {
                    Request next;
                    if (extractMin(&h, &next))
                        printf("Auto cleaned Bin ID:%d (%s)\n", next.id, next.area);
                    else printf("No bins to clean.\n");
                }
                else if (choice == 6) adminChooseBin(&h);
                else if (choice == 7) break;
                else printf("Invalid choice.\n");
            }
        }

        else if (role == 2) {
            while (1) {
                printf("\n===== User Menu =====\n");
                printf("1. Add Bin Request\n");
                printf("2. Display Queue\n");
                printf("3. Logout to Main Menu\n");
                printf("Enter choice: ");
                scanf("%d", &choice);

                if (choice == 1) {
                    Request r;
                    printf("Enter Bin ID: ");
                    scanf("%d", &r.id);
                    if (idExists(&q, &h, r.id)) {
                        printf("Bin ID already exists! Try another.\n");
                        continue;
                    }
                    printf("Enter Area: ");
                    scanf("%29s", r.area); // Prevents writing beyond the 30-byte buffer
                    printf("Enter Fill Level (0-100): ");
                    scanf("%d", &r.fill);
                    if (r.fill < 0) r.fill = 0;
                    if (r.fill > 100) r.fill = 100;
                    r.priority = 100 - r.fill; //!priority set
                    enqueue(&q, r);
                }
                else if (choice == 2) displayQueue(&q);
                else if (choice == 3) break;
                else printf("Invalid choice.\n");
            }
        }

        else if (role == 3) {
            printf("Exiting program...\n");
            break;
        }
        else printf("Invalid choice! Try again.\n");
    }

    free(h.arr);
    Node *cur = q.front;
    while (cur) {
        Node *tmp = cur;
        cur = cur->next;
        free(tmp);
    }

    printf("Program ended.\n");
    return 0;
}
