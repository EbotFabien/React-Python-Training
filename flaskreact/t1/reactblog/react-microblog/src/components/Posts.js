import { useState,useEffect } from "react";
import Spinner from 'react-bootstrap/Spinner';
import { useApi } from "../contexts/ApiProvider";
import Post from './Post';
import More from './More';
import Write from './Write';


export default function Posts({content,write}){
    const [posts,setPosts] = useState();
    const [pagination,setPagination] = useState();
    const api=useApi()

    //TODO: add a side effect function to request posts here
    let url;
    switch (content){
      case 'feed':
      case undefined:
        url = '/feed';
        break;
      case 'explore':
        url = '/posts';
        break
      default:
        url = `/users/${content}/posts`;
        break;
    }
    useEffect(()=>{
      (async () => {
        const response = await api.get(url);
        if (response.ok){
          setPosts(response.body.results);
          setPagination(response.body.pagination);
        }
        else{
          setPosts(null)
        }
      })();
    },[api,url]);

    const showPost = (newPost) =>{
        setPosts([newPost,...posts])
    };

    const loadNextPage = async () =>{
        const response = await api.get(url,{
          page:pagination.page + 1
        });
        if (response.ok){
          setPosts([...posts,...response.body.results]);
          setPagination(response.body.pagination);
        }
    };

    return(
      <>  
          {write && <Write showPost={showPost} />}
          {posts ===  undefined?
              <Spinner animation="border"/>
          :
          <>
          {posts === null ?
            <p>Could not retrieve blog posts .</p>
          :
            posts.map(post=> <Post key={post.id} post={post}/>)
          }
          <More pagination={pagination} loadNextPage={loadNextPage} />
          </>
              
          
          }
      </>
    )
}