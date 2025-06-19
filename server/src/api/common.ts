export async function catchError<T>(promise: Promise<T>): Promise<[Error] | [undefined, T]> {
    return promise
        .then((data: T) => [undefined, data] as [undefined, T])
        .catch((error: Error) => [error])
}
